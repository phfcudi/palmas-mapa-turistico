# Fontes, créditos e licenças

## Resumo
| Fonte | Usada para | No repositório? | Licença / observação |
|---|---|---|---|
| **OpenStreetMap** (3 exportações Overpass) | Rodovias, rios, polígonos (aeroporto, ATA, Agrotins, aterro, lago, estádio…), alamedas, residenciais | Sim — `data/raw/osm/` | ODbL 1.0 — © colaboradores do OpenStreetMap |
| **Imagens-base** (7 capturas do mapa padrão do OSM, montadas no CorelDRAW) | Fundo do mapa 2D e chão do 3D | Sim — `data/base/tiles/` | Dados ODbL; estilo cartográfico CC BY-SA 2.0 (política de tiles do OSM) |
| **Esquema de quadras do Plano Diretor** (GIF, ex.: `604 S (ARSE 61)`) | Contorno aproximado e códigos novo/antigo das quadras | **Não** (`data/external/`) | Material de terceiros; só os resultados derivados (nomes e posições) foram usados |
| **Mapa turístico de Palmas** (PDF; designer citado no próprio arquivo: Dimensão) | Conferir códigos de quadras; fatos nas fichas (Graciosa, Cesamar, Taquaruçu, Lago, Mirante da Serra); posição aproximada de pontos | **Não** | Fotos, ilustrações e logotipo **não** foram copiados. Os fatos aparecem com a indicação “Fonte: mapa turístico de Palmas fornecido” |
| **Google Maps** (captura de tela fornecida) | Endereço, telefone e site do CATUR central | **Não** | Apenas fatos (endereço/telefone); o horário exibido pode mudar |
| **Jornal Opção Tocantins** (11/04/2025) | Inauguração do CATUR no aeroporto | Não (link na ficha) | Citado como fonte |
| Resumo “AI Overview” do Google | Existência das unidades CATUR (aeroporto, Taquaruçu) | Não | **Não verificado em fonte oficial**; a ficha avisa |
| **Three.js r128** | Modo 3D | Não (carregado do cdnjs) | MIT |
| **Bricolage Grotesque** (Google Fonts) | Tipografia de títulos | Não (carregada do Google Fonts) | SIL OFL 1.1 |

## Atribuições obrigatórias
* “Base cartográfica © colaboradores do OpenStreetMap” — já exibida no rodapé do painel; **não remova**.
* Ao reutilizar `data/raw` ou `data/processed`, mantenha a atribuição e a licença ODbL (ver `data/LICENSE-DATA.md`).

## O que precisa de autorização antes de entrar no projeto
* **Fotos e logotipo** do mapa turístico e da Prefeitura (identidade visual oficial): peça autorização ao titular.
* **Marcas** de empresas e instituições citadas (SESC, SEBRAE, ULBRA, Católica etc.) aparecem apenas como **nome de local**.
  Não inclua logotipos sem permissão.

## Pendências de licenciamento (decisões do mantenedor)
1. Preencher o titular em `LICENSE` (`<NOME OU ORGANIZAÇÃO>`).
2. Definir a licença das contribuições originais dos dados (sugestão: ODbL ou CC BY-SA 4.0).
3. Conferir se a Prefeitura/Agtur quer ser creditada como referência do conteúdo turístico.
