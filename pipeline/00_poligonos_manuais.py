"""Extrai os contornos desenhados à mão (Taquaralto, Taquarussu, Capivara) de src/build.py
e grava data/processed/hand_polys.json (em unidades do SVG). Usado nos passos 06 e 07 como
referência para verificar contornos gerados a partir de dados do OpenStreetMap."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL, SRC ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/

import json
src = open(SRC / "build.py", encoding="utf-8").read()
head = src[: src.index("# ---------- geometrias reais do OpenStreetMap")]   # só a parte desenhada à mão
ns = {"__file__": str(SRC / "build.py")}
exec(compile(head, "build_head", "exec"), ns)
R, u = ns["R"], ns["u"]
H = {}
for r in R:
    if r["id"] in ("taquaralto", "taquarussu", "capivara"):
        k, t, p = max([x for x in r["parts"] if x[0] == "a"], key=lambda x: len(x[2]))
        H[r["id"]] = [u(t, *q) for q in p]
json.dump(H, open("hand_polys.json", "w", encoding="utf-8"))
print({k: len(v) for k, v in H.items()})
