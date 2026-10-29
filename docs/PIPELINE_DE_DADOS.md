# Pipeline de dados

Os dados do mapa não foram digitados um a um: vêm de **exportações do OpenStreetMap**, de um **mapa esquemático das quadras**
e de **contornos traçados à mão**, combinados por scripts numerados em `pipeline/`. Todos os passos de 00 a 07
foram **reexecutados do zero e regeneram exatamente os arquivos versionados** em `data/processed/`.

## Visão geral

| # | Script | Entradas | Saídas (em `data/processed/`) | O que faz |
|---|---|---|---|---|
| 00 | `00_poligonos_manuais.py` | `src/build.py` (parte manual) | `hand_polys.json` | Extrai os contornos manuais de Taquaralto, Taquarussu e Capivara para comparação |
| 01 | `01_segmentar_esquema.py` | GIF em `data/external/` + `tesseract` | `cells.json` | Separa cada quadra do esquema por cor e lê os rótulos por OCR |
| 02 | `02_georreferenciar_esquema.py` | `cells.json`, `manc.json` | `quadras_raw.json` | Dá nome às células (transcrição manual no norte, regra de numeração no sul) e as encaixa no mosaico |
| 03 | `03_refs_quadras_osm.py` | `osm_export_1.geojson` | `osm_q.json` | Agrupa as ruas citando a quadra ("Alameda 01 Quadra 812 Sul") |
| 04 | `04_calibrar_osm.py` | `quadras_raw.json`, `osm_q.json`, `tile_1.png` | `init.npy`, `Wi.npy` | Calibra lon/lat → mosaico (afim inicial + refino ECC sobre as ruas) |
| 05 | `05_refinar_quadras.py` | passos 02–04 + `osm_export_1` | `quadras_final.json`, `lazer.json` | Reposiciona quadras com as alamedas, completa as que faltavam e extrai polígonos de lazer |
| 06 | `06_osm_para_regioes.py` | `osm_export_2`, `hand_polys.json`, calibração | `osm_regs.json` | Polígonos reais (aeroporto, ATA, Agrotins, aterro, lago), rodovias, rios, POIs |
| 07 | `07_osm_regioes_extra.py` | `osm_export_3`, `hand_polys.json`, `quadras_final.json` | `osm_regs2.json`, `quadra_fix.json` | Ferrovia, terminal, equipamentos, residenciais nomeados e correção de contornos de quadras |
| – | `src/build.py` | tudo acima + imagens | `dist/index.html` | Gera o mapa |

Execute a partir da raiz, nesta ordem, com `PYTHONUTF8=1` no Windows:
```bash
pip install -r requirements-pipeline.txt
python pipeline/03_refs_quadras_osm.py
python pipeline/04_calibrar_osm.py          # ~1 min (otimização ECC)
python pipeline/05_refinar_quadras.py
python pipeline/06_osm_para_regioes.py
python pipeline/07_osm_regioes_extra.py
python src/build.py
```
Os passos 01 e 02 só são necessários se você quiser refazer a leitura do esquema de quadras
(exigem o GIF de terceiros em `data/external/` e o programa `tesseract`).

## Calibração (como lon/lat viram posições no mosaico)
1. As 7 imagens são capturas do mesmo mapa (mesma escala) posicionadas à mão no CorelDRAW; o layout está em
   `data/base/mosaico_original.svg` e em `src/calib.py` (`TILES`).
2. Uma **transformação afim** lon/lat → pixels da imagem 1 é ajustada por mínimos quadrados, usando o centro de
   dezenas de quadras (nome + alamedas do OSM). Em seguida um refino **ECC** (OpenCV) alinha as ruas do OSM às
   ruas da imagem (`init.npy` e `Wi.npy`).
3. `calib.g_units(lonlat)` aplica as duas etapas e devolve as unidades do mosaico.
4. **Validação**: 16 pontos de referência espalhados pelas 7 imagens (ATA, aterro, Agrotins, Luzimangues, Taquarussu,
   Capivara…) ficaram, na maioria, a menos de ~12 px da posição vista na imagem (precisão da leitura).
   Uma única calibração vale para todo o mosaico (não foi necessária correção por imagem).

## Quadras do Plano Diretor
* **Geometria**: células segmentadas do esquema (passo 01) → posição no mosaico por faixas (cada faixa entre avenidas LO)
  e colunas (eixo Teotônio Segurado) → ajuste fino com as **alamedas** do OSM (passo 05): cada quadra é deslocada
  para conter o máximo de alamedas que citam seu número; movimentos que criam sobreposição são revertidos.
* **Nomes**: no norte, transcritos à mão do esquema/PDF (`manc.json`); no sul, regra de numeração validada contra o
  esquema, o PDF turístico e o OSM. Quadras que o OSM cita e o esquema não segmentou entram por **envoltória das
  alamedas** só quando o formato é plausível.
* **Cobertura**: 154 quadras. Algumas ficaram de fora por não terem sido isoladas no esquema; ver `LIMITACOES.md`.

## Consultas do Overpass Turbo usadas nas exportações
As exportações foram feitas pelo site https://overpass-turbo.eu (Exportar → GeoJSON). As consultas abaixo são as **sugeridas durante o projeto**; o histórico exato do que foi executado em cada exportação não foi guardado (a área coberta por `osm_export_2` é maior que a do mosaico: lon −48,59…−47,82; lat −10,88…−9,74). Em resumo:

* **`osm_export_1`** — elementos com nome de quadra/ARSE/ARNE… na área do Plano Diretor (alamedas, polígonos de lazer, feira):
  ```
  [out:json][timeout:90];
  ( way["name"~"Quadra|ARSE|ARSO|ARNE|ARNO|ASR|ACSU|[0-9]{3,4} (Sul|Norte)"](-10.32,-48.40,-10.10,-48.28);
    relation["name"~"Quadra|ARSE|ARSO|ARNE|ARNO|ASR|ACSU|[0-9]{3,4} (Sul|Norte)"](-10.32,-48.40,-10.10,-48.28); );
  out geom;
  ```
* **`osm_export_2`** — arredores (localidades, aeródromos, rodovias, usos do solo, água); a versão com `{{bbox}}` pode ser rodada por partes se o servidor recusar a área toda:
  ```
  [out:json][timeout:60];
  ( nwr["place"~"city|town|village|hamlet|suburb|neighbourhood|locality"]({{bbox}});
    nwr["aeroway"~"aerodrome|runway"]({{bbox}});
    way["railway"="rail"]({{bbox}});
    way["highway"~"motorway|trunk|primary|secondary"]({{bbox}});
    nwr["landuse"~"industrial|farmland|farmyard|military|landfill|depot"]["name"]({{bbox}});
    nwr["natural"="water"]["name"]({{bbox}}); );
  out geom;
  ```
* **`osm_export_3`** — ferrovia, nomes específicos e áreas residenciais:
  ```
  [out:json][timeout:90];
  ( way["railway"~"rail|construction|proposed"](-10.45,-48.60,-10.05,-48.10);
    nwr["name"~"Frigovale|Prata|Terminal|Multimodal|Capivara|Taquaralto"](-10.45,-48.60,-10.05,-48.10);
    way["landuse"="residential"](-10.45,-48.60,-10.05,-48.10); );
  out geom;
  ```
Atenção: o conteúdo do OSM muda com o tempo. Refazer as exportações pode alterar o resultado; confira o diff de `data/processed/`.

## Atualizar os dados
1. Substitua os arquivos de `data/raw/osm/` por novas exportações.
2. Rode os passos 03 → 07 e `python src/build.py`.
3. Revise as diferenças (`git diff --stat data/processed`) e abra o mapa para conferir visualmente.
