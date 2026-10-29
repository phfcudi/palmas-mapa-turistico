# Como editar

Depois de qualquer mudança: `python src/build.py` e abra `dist/index.html`. Rode `pytest` antes de publicar.

## Adicionar ou corrigir um ponto turístico
Os pontos estão em `src/build.py`, na seção `# ---------- pontos turísticos (...) ----------` e nos blocos seguintes
(`cinco pontos adicionais`, `mais seis pontos…`, etc.). Cada ponto é uma tupla na lista `NEW` (ou `SIGNS`, para placas de destino):

```python
NEW += [(
    'tur-meu-ponto',                      # id único (prefixo "tur-")
    'Nome completo do ponto',             # título da ficha
    'umbrella',                           # ícone (ver lista em MODELO_DE_DADOS.md)
    'lago',                               # grupo/tema: lago, cult, nat, esp, trans, serv, sign
    tuple(u(1, 145, 1085)),               # posição em unidades (ver "Posições" abaixo)
    'Descrição para a ficha. Fonte e grau de certeza.',
    'Rótulo curto',                       # texto exibido no marcador
)]
```
Depois **registre o marcador** na lista `MKDEF` (mesma seção): `('tur-meu-ponto', 'umbrella', 'lago')`.
Para entrar no tour, acrescente o id em `const TOUR=[…]` no `src/template.html`.

### Posições (âncoras)
| Ajudante | Uso |
|---|---|
| `u(tile, px, py)` | Pixel de uma imagem (largura de referência 1110 px) → unidades. `tile` é 1…7 (ver `TILES`) |
| `_qc('103 N', 'ACNO 1')` | Centro de uma quadra do Plano Diretor (o segundo argumento desempata códigos repetidos) |
| `_edge('504 N', 'w', 3, dx)` | Borda oeste (`'w'`) ou leste (`'e'`) de uma quadra, com deslocamento `dx` em pixels |
| `_rc('id-da-região')` | Centro de uma região existente (ex.: `_rc('taquarussu')`) |
| coordenadas diretas | Uma tupla `(x, y)` em unidades |

**Dica**: abra `dist/index.html`, dê zoom no local e use o console do navegador: `vb` mostra a vista atual; ou calcule
`u(1, px, py)` a partir de um pixel da imagem 1.

## Mudar texto de um local existente
Use `_upd('id-da-região', 'novo texto')` (veja o bloco `_upd(...)` na seção de turismo). Textos de regiões desenhadas à mão
ficam nas chamadas `add(...)` no início do `build.py`.

## Adicionar um ícone
1. No `src/template.html`, acrescente o caminho SVG (grade 24×24, traço) em `const ICO={…}`.
2. Use o nome do ícone no ponto (campo `ic`).

## Adicionar um tema (grupo) de marcadores
Em `src/template.html`: inclua a cor em `const GRP={…}` e uma linha em `const GN=[…]` (chave, nome, ícone).

## Atualizar contornos e vias
Edite/gere novos dados do OpenStreetMap e rode o pipeline (`docs/PIPELINE_DE_DADOS.md`). Não edite `data/processed/*.json` à mão:
eles são regenerados pelos scripts.

## Trocar as imagens-base
1. Substitua `data/base/tiles/tile_N.png` mantendo a posição no mosaico (`TILES` em `src/calib.py` e `src/build.py`).
2. Se a escala/posição mudar, refaça a calibração (passo 04).
