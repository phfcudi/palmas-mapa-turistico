"""Testes de integridade do mapa gerado e da calibração. Rode com: pytest"""
import json, re, shutil, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(scope="session")
def html():
    subprocess.run([sys.executable, str(ROOT / "src" / "build.py")], check=True, cwd=ROOT)
    return (ROOT / "dist" / "index.html").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def D(html):
    m = re.search(r"const D=(\{.*?\});\nconst \$", html, re.S)
    assert m, "dados não encontrados no HTML"
    return json.loads(m.group(1))


def test_sem_marcadores_de_posicao_pendentes(html):
    assert "__IMAGES__" not in html and "__DATA__" not in html


def test_atribuicao_openstreetmap(html):
    assert "OpenStreetMap" in html


def test_ids_de_regioes_unicos(D):
    ids = [r["id"] for r in D["regs"]]
    assert len(ids) == len(set(ids)), "há ids de região repetidos"


# Regiões ilustrativas que ficam de propósito fora das imagens-base (ver docs/LIMITACOES.md)
FORA_DO_MOSAICO = {"tur-serra"}


def test_regioes_validas(D):
    assert len(D["regs"]) >= 300
    for r in D["regs"]:
        assert r["c"] in D["cats"], r["id"]
        assert r["p"], f"{r['id']} sem geometria"
        x0, y0, x1, y1 = r["bb"]
        assert x0 <= x1 and y0 <= y1
        if r["id"] not in FORA_DO_MOSAICO:
            assert -2000 <= x0 and x1 <= 136000 and -500 <= y0 and y1 <= 134500, f"{r['id']} fora do mosaico"
        for p in r["p"]:
            assert p["k"] in ("a", "l")
            assert len(p["q"]) >= (3 if p["k"] == "a" else 2), r["id"]


def test_marcadores_apontam_para_regioes(D):
    ids = {r["id"] for r in D["regs"]}
    mk_ids = [m["id"] for m in D["mk"]]
    assert len(mk_ids) == len(set(mk_ids)), "marcador duplicado"
    assert len(D["mk"]) >= 35
    for m in D["mk"]:
        assert m["id"] in ids, m["id"]
        assert m["g"] in ("lago", "cult", "nat", "esp", "trans", "serv", "sign")


def test_icones_dos_marcadores_existem_no_template(D, html):
    for m in D["mk"]:
        if m["ic"] != "sign":
            assert re.search(r"\b" + re.escape(m["ic"]) + r":'M", html), f"ícone {m['ic']} sem desenho"


def test_codigos_de_quadras(D):
    q = [r for r in D["regs"] if r["c"] == "q"]
    assert len(q) >= 150
    assert any(r.get("o") == "ARSE 61" for r in q), "604 S (ARSE 61) deveria existir"
    # há códigos novos repetidos de propósito (ex.: 104 N); o id deve diferenciá-los
    assert len({r["id"] for r in q}) == len(q)


def test_calibracao_praca_dos_girassois():
    from calib import g_units
    x, y = g_units([-48.3336, -10.1838])[0]          # Praça dos Girassóis
    assert abs(x - 76200) < 2500 and abs(y - 26800) < 2500


def test_sintaxe_javascript(html):
    node = shutil.which("node")
    if not node:
        pytest.skip("node não instalado")
    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    assert len(scripts) == 2
    for i, js in enumerate(scripts):
        js = js.replace("addEventListener('hashchange'", "0&&addEventListener('hashchange'")
        r = subprocess.run([node, "-e", "new Function(require('fs').readFileSync(0,'utf8'))"], input=js, text=True, capture_output=True)
        assert r.returncode == 0, f"script {i}: {r.stderr[:300]}"
