# Arquitetura

O resultado é **um único arquivo HTML** (`dist/index.html`) que contém tudo: as imagens-base em WebP/base64,
os dados (JSON) e o código (HTML + CSS + JavaScript). Não há servidor nem banco de dados.

```
imagens-base (7 PNG) ─┐
dados processados     ├─► src/build.py ─► dist/index.html
src/template.html ────┘
```

## 1. Geração (`src/build.py`)

1. Converte as 7 imagens para WebP (com um realce de cor/contraste "turístico") e as insere em um SVG.
2. Monta a lista de **regiões** (`D.regs`): áreas desenhadas à mão + geometrias do OpenStreetMap +
   quadras do Plano Diretor + pontos turísticos. Aplica as substituições de geometria real sobre os contornos manuais.
3. Calcula, para cada região, a caixa envolvente (`bb`) e o ponto de rótulo (`lab`), e os **marcadores** (`D.mk`).
4. Injeta imagens (`__IMAGES__`) e dados (`__DATA__`) em `src/template.html` e grava `dist/index.html`.

## 2. Sistema de coordenadas

* Tudo usa as **unidades do SVG original do CorelDRAW** (`data/base/mosaico_original.svg`): cada imagem é um
  retângulo posicionado em unidades. **1 unidade ≈ 0,37 m** (medido pela barra de escala das imagens).
* O mosaico cobre x ∈ [−912; 134 655] e y ∈ [0; 133 742]. O norte é para cima (y cresce para o sul).
* Dados do OpenStreetMap (lon/lat) entram por `src/calib.py → g_units()` (calibração afim; ver `PIPELINE_DE_DADOS.md`).

## 3. Interface (`src/template.html`)

O arquivo tem três partes:

| Parte | Conteúdo |
|---|---|
| `<style>` | Temas claro/escuro (variáveis CSS), painel lateral, marcadores, banner, bússola, tour, menu retrátil, responsivo |
| `<script>` nº 1 | Dados, **motor 2D**, painel (lista, busca, filtros, ficha), marcadores, destaques, tour guiado, menu retrátil |
| `<script>` nº 2 | **Módulo 3D** (IIFE): carrega o Three.js sob demanda e monta a cena |

### Motor 2D
* O mapa é um `<svg>` com 7 `<image>` e uma camada de regiões (`<path>`). Zoom e arrasto mudam o `viewBox`.
* **Regiões**: cada uma é um `<g class="rg c{categoria}">` com um ou mais caminhos (`a` = área, `l` = linha).
  Estilo por categoria via variáveis CSS (`--b`, `--p`, `--i`, `--n`, `--v`, `--q`, `--l`, `--t`).
* **Visibilidade por zoom**: quadras só aparecem com `vb.w < 38 000`; lazer com `vb.w < 14 000`; rótulos
  dependem do tamanho da região na tela.
* **Marcadores** são botões HTML posicionados sobre o SVG por projeção linear (`placeMk`), compartilhados com o 3D.
* **Voo da câmera** (`fly`): se o destino está longe da vista atual, a largura da vista passa por um pico
  (zoom out), a câmera se desloca e então aproxima (zoom in).
* Gestos: arrastar, roda do mouse e pinça (ponteiros do navegador, sem bibliotecas).

### Painel
Busca (sem acento), filtros por categoria e por tema, lista, ficha da região, atalhos de bairro, cartões de
destaque e **tour guiado**. É **retrátil**: a aba na borda alterna a coluna (`grid-template-columns`) e, no celular,
a linha (`grid-template-rows`). A escala do mapa é preservada ao redimensionar.

### Módulo 3D
* **Three.js r128** carregado de `cdnjs` na primeira vez que o usuário clica em 3D (falha → aviso, sem quebrar o 2D).
* **Chão**: 7 planos com as imagens-base (mesma ordem de sobreposição do SVG original).
* **Regiões**: extrusões **achatadas e translúcidas** (relevo fixo em 0) para bairros, quadras, etc.; linhas para vias e rios.
  Seleção realça a região. Raycasting para clique e dica (tooltip).
* **Cenário**: céu em domo com sol, **Serra do Lajeado** (malha procedural), ~1 700 árvores instanciadas, nuvens,
  água com reflexos animados, 6 barcos, 5 parapentes, 4 aviões, palmeiras nas praias e monumentos simples
  (Palácio Araguaia, Ponte, Estádio, Aeroporto, Rodoviária).
* **Câmera**: órbita própria (arrastar = girar, botão direito/Shift/dois dedos = mover, roda/pinça = zoom),
  presets (Turística, Topo, Inclinada, Perspectiva, Rasante) e animação com a mesma curva zoom out/in.
* **Desempenho**: animação limitada a ~33 quadros/s; botão **Animação** desliga o movimento (render sob demanda).

## 4. Restrições de hospedagem
A página foi pensada para rodar em hospedagens estáticas com política de segurança restrita: o único
conteúdo externo é o script do Three.js (cdnjs) e a fonte (Google Fonts), ambos com fallback.
Não usa `localStorage` nem APIs de rede para dados.

## 5. Mapa do código do `template.html`
| Procurar por | O que é |
|---|---|
| `const D=__DATA__` | Dados injetados |
| `function fly(` | Animação 2D da câmera (zoom out → pan → zoom in) |
| `function select(` | Seleção de região (ficha, câmera, destaque) |
| `buildMarkers` / `placeMk` | Marcadores HTML (2D) |
| `const HLS` / `const TOUR` | Cartões de destaque e roteiro do tour |
| `setPanel(` | Menu retrátil |
| `function scenery(` / `landmarks(` / `sky3(` / `water(` / `boats3(` / `gliders3(` / `plane3(` / `palms(` | Cenário 3D |
| `function go(` | Animação da câmera 3D |
| `PRE =` / `turPreset(` | Atalhos de ângulo 3D |
