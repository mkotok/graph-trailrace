import decoder
import globalmaptiles
import requests


def get_tile(tileset_id, x, y, zoom):
    # https://docs.mapbox.com/api/maps/vector-tiles
    url = f"https://api.mapbox.com/v4/{tileset_id}/{zoom}/{x}/{y}.mvt"
    url += "?access_token=pk.eyJ1IjoidHJhaWxzcm9jIiwiYSI6ImNqOW94MjB2dTVraDYycW5yZmtxZ3ljNTUifQ.-servtc1C9TmiyDbmPCx_g"    
    with requests.get(url) as resp:
        if resp.status_code != 200:
            raise Exception((resp.status_code, resp.reason))
        else:
            return decoder.decode(resp.content)

        
def get_mponds_tiles(zoom):
    # https://www.maptiler.com/google-maps-coordinates-tile-bounds-projection/#13/-77.55/43.02
    mercator = globalmaptiles.GlobalMercator(tileSize=4096)
    tl_x, tl_y = mercator.LatLonToGoogleTile(43.045247, -77.585596, zoom)
    br_x, br_y = mercator.LatLonToGoogleTile(42.996604, -77.542743, zoom)
    
    TX = list(range(tl_x, br_x+1))
    TY = list(range(br_y, tl_y-1, -1))
    return TX, TY


class TrailSegment:
    def __init__(self, fdict):
        geometry = fdict["geometry"]
        props = fdict["properties"]
        assert props["trailsroc-type"] == "trailSegment"
        self.id = props["trailsroc-id"]
        self.color = props.get("trailsroc-color", "unmarked_trail")
        self.name = props.get("trailsroc-name", "Unknown")
        if geometry["type"] == "LineString":
            self.coords = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            self.coords = geometry["coordinates"]
        else:
            raise Exception("Unknown geometry type: " + geometry["type"])
            
    def clip(self, w, h):
        for i in range(len(self.coords)-1, -1, -1):
            for j in range(len(self.coords[i])-1, -1, -1):
                x, y = self.coords[i][j]
                if x < 0 or y < 0 or x > w or y > h:
                    del self.coords[i][j]
            if len(self.coords[i]) == 0:
                del self.coords[i]
        return self
    
    def shift(self, xs, ys):
        for i in range(len(self.coords)):
            for j in range(len(self.coords[i])):
                assert len(self.coords[i][j]) == 2
                self.coords[i][j][0] += xs
                self.coords[i][j][1] += ys
        return self
