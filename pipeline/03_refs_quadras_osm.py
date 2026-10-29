"""Lê os nomes das ruas do primeiro export do OSM (ex.: "Alameda 01 Quadra 812 Sul") e agrupa as
coordenadas por quadra -> data/processed/osm_q.json. Serve para validar nomes e posições das quadras."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL, SRC ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/

import json, re, collections
d = json.load(open(RAW / "osm_export_1.geojson", encoding="utf-8"))
def pts(g):
    if g["type"] == "LineString": return g["coordinates"]
    if g["type"] == "Polygon": return g["coordinates"][0]
Q = collections.defaultdict(list)
rx = re.compile(r"(?:Quadra|Qd|Qadra)?\s*0*(\d{3,4})\s*(Sul|Norte)\b", re.I)
for f in d["features"]:
    n = f["properties"].get("name", "")
    for m in rx.finditer(n):
        side = "S" if m.group(2).lower() == "sul" else "N"
        Q[f"{int(m.group(1))}{side}"].extend(pts(f["geometry"]))
json.dump(Q, open("osm_q.json", "w", encoding="utf-8"))
print("quadras citadas:", len(Q))
