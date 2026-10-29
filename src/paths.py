"""Caminhos do repositório. Todos relativos à raiz, para o projeto rodar em qualquer máquina."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DATA = ROOT / "data"
TILES_DIR = DATA / "base" / "tiles"      # 7 capturas do mapa-base (OpenStreetMap)
RAW = DATA / "raw" / "osm"               # exportações GeoJSON do Overpass Turbo
PROC = DATA / "processed"                # dados derivados (JSON) e calibração
EXTERNAL = DATA / "external"             # arquivos de terceiros, NÃO versionados (ver docs/FONTES_E_LICENCAS.md)
DIST = ROOT / "dist"                     # saída: dist/index.html
