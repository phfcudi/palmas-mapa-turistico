"""Teste de fumaça no navegador (Playwright). Pulado se o Playwright não estiver instalado.
O 3D é testado com um Three.js simulado (tests/mock3.js), pois o teste roda sem internet."""
from pathlib import Path
import pytest

pw = pytest.importorskip("playwright.sync_api")
ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dist" / "index.html"


@pytest.fixture()
def page():
    if not INDEX.exists():
        pytest.skip("rode `python src/build.py` antes")
    with pw.sync_playwright() as p:
        try:
            b = p.chromium.launch(args=["--no-sandbox"])
        except Exception as e:                                   # navegador não instalado
            pytest.skip(f"chromium indisponível: {e}")
        pg = b.new_page(viewport={"width": 1300, "height": 820})
        pg.errors = []
        pg.on("pageerror", lambda e: pg.errors.append(str(e)))
        mock = (ROOT / "tests" / "mock3.js").read_text(encoding="utf-8")
        pg.route("**/three.min.js", lambda r: r.fulfill(status=200, content_type="application/javascript", body=mock))
        pg.goto(INDEX.as_uri())
        pg.wait_for_timeout(1200)
        yield pg
        b.close()


def test_carrega_sem_erros_e_com_marcadores(page):
    assert page.locator(".mk").count() >= 35
    assert page.locator(".rg").count() >= 300
    assert page.errors == []


def test_menu_retratil(page):
    page.click("#pt")
    page.wait_for_timeout(500)
    assert page.evaluate("document.querySelector('.app').classList.contains('col')")
    page.evaluate("select('tur-ponte')")            # escolher um ponto reabre o menu
    page.wait_for_timeout(300)
    assert not page.evaluate("document.querySelector('.app').classList.contains('col')")
    assert page.errors == []


def test_tour_e_modo_3d(page):
    page.click("#tgo")
    page.wait_for_timeout(1500)
    assert "1/" in page.inner_text("#tt")
    page.click("#tx")
    page.click("#m3")                                # 3D (com Three.js simulado)
    page.wait_for_timeout(1500)
    assert page.evaluate("V3.on")
    for pre in ("tur", "topo", "incl", "persp", "ras"):
        page.click(f'[data-pre="{pre}"]')
    page.click("#m3")
    assert page.errors == []
