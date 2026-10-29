# data/external — arquivos de terceiros (não versionados)

Esta pasta fica **vazia no repositório** de propósito. Alguns insumos usados na criação dos dados
são de terceiros e não têm licença de redistribuição clara. Para refazer o **passo 01** do pipeline
(`pipeline/01_segmentar_esquema.py`), coloque aqui:

| Arquivo | Para que serve | Onde obter |
|---|---|---|
| `mapa_de-palmas-plano-diretor-com-quadras.gif` | Mapa esquemático do Plano Diretor com os códigos novo/antigo de cada quadra (ex.: `604 S (ARSE 61)`) | Material de divulgação do Plano Diretor de Palmas (peça de terceiros) |

O resultado desse passo (`data/processed/cells.json`) **já está versionado**, então só é preciso o GIF
se você quiser refazer a segmentação das quadras do zero.

Também **não** estão no repositório: o PDF do mapa turístico (fotos e logotipo da Prefeitura) e capturas
de tela do Google Maps. Veja `docs/FONTES_E_LICENCAS.md`.
