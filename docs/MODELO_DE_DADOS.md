# Modelo de dados

Os dados ficam embutidos no HTML como `const D = { cats, regs, mk }`. Eles são montados por `src/build.py`.

## Sistema de coordenadas
Unidades do SVG original (1 unidade ≈ 0,37 m); x cresce para leste e y para o sul. Ver `ARQUITETURA.md`.

## `D.cats` — categorias de região
| Chave | Nome | Cor (tema claro) | Observação |
|---|---|---|---|
| `t` | Pontos turísticos | `#d99100` | Só aparecem como marcador (polígono oculto) |
| `b` | Bairros e localidades | `#13917f` | |
| `p` | Pontos de interesse | `#df5f22` | |
| `i` | Infraestrutura | `#6f4fd0` | Aeroportos, terminais, aterro etc. |
| `n` | Natureza e água | `#1f7fcb` | Lago, rios, matas |
| `v` | Vias e ferrovia | `#bd3a2a` | Linhas |
| `q` | Quadras do Plano Diretor | `#b88600` | Só visíveis com zoom; entram na busca |
| `l` | Lazer e esportes | `#c2255c` | Só visíveis com muito zoom; entram na busca |

## `D.regs[]` — regiões clicáveis
| Campo | Tipo | Descrição |
|---|---|---|
| `id` | string | Identificador único (usado em `#hash`, busca e marcadores) |
| `n` | string | Nome completo exibido na ficha |
| `c` | string | Categoria (`D.cats`) |
| `d` | string | Descrição (texto da ficha) |
| `p` | lista | Partes da geometria: `{ "k": "a" \| "l", "q": [[x,y], …] }` — `a` = área (polígono), `l` = linha |
| `bb` | `[x0,y0,x1,y1]` | Caixa envolvente (calculada) |
| `lab` | `[x,y]` | Ponto do rótulo (calculado) |
| `s` | string (opcional) | Rótulo curto |
| `f` | número (opcional) | Opacidade do preenchimento em % (padrão 20) |
| `o` | string (opcional) | Código antigo da quadra (ex.: `ARSE 61`) |
| `ln` | `1` (opcional) | Região só de linhas (rios, vias): rótulo aparece só com zoom |

Exemplo (quadra, com a geometria abreviada):
```json
{
  "id": "q-605-norte-arno-72",
  "n": "Quadra 605 Norte (ARNO 72)",
  "c": "q",
  "d": "Quadra residencial (ARNO 72, Área Residencial Norte Oeste). Contorno e posição aproximados, derivados do mapa esquemático de quadras de Palmas e ajustados pelas alamedas do OpenStreetMap.",
  "p": [
    {
      "k": "a",
      "q": [
        [
          77474,
          16008
        ],
        [
          77298,
          15970
        ],
        "…"
      ]
    }
  ],
  "bb": [
    75874,
    15970,
    77474,
    17329
  ],
  "lab": [
    76674,
    16650
  ],
  "s": "605 N",
  "f": 14,
  "o": "ARNO 72"
}
```

## `D.mk[]` — marcadores turísticos
| Campo | Descrição |
|---|---|
| `id` | Id da região associada (a ficha aberta ao clicar) |
| `ic` | Ícone (`bridge`, `palace`, `sunflower`, `tree`, `cap`, `umbrella`, `island`, `wave`, `stadium`, `flag`, `plane`, `bus`, `wheat`, `waterfall`, `mountain`, `market`, `building`, `info`, `bag`, `theater`, `health`, `sign`) |
| `g` | Grupo/tema: `lago`, `cult`, `nat`, `esp`, `trans`, `serv`, `sign` |
| `x`, `y` | Posição (ponta do pin) em unidades |
| `s` | Rótulo exibido |

Cores dos grupos: `lago #1f7fcb`, `cult #b0359f`, `nat #2f9e44`, `esp #e2692c`, `trans #5b6b72`, `serv #0e9aa7`, `sign #f6c71c`.

Exemplo:
```json
{
  "id": "tur-sesc",
  "ic": "building",
  "g": "cult",
  "x": 80303,
  "y": 20589,
  "s": "SESC"
}
```

## Numeração das quadras (convenção usada)
* **Código novo**: `BNN S|N` — `B` é a faixa (centenas), `NN` a coluna. **Ímpar = oeste** e **par = leste** da
  Av. Teotônio Segurado; **Norte/Sul** são separados pela Av. JK. Ex.: `604 S`.
* **Código antigo**: `ARSO/ARSE/ARNO/ARNE + faixa + índice` (ex.: `ARSE 61`), `ASR-SE/ASR-NE` (faixa de serviços na borda
  leste), `ACSU-*` (faixas comerciais ao longo da Teotônio Segurado) e `AC*`/`AA-*` (áreas centrais e da Praça).
* **Há códigos novos repetidos** (ex.: duas `104 N`: `ACNE 1` e `ACNE 11`); por isso o `id` combina o código novo
  e o antigo (`q-104-n-acne-1`).
