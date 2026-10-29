# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versionamento semântico.

## [1.0.0] — 2026-10-27
Primeira versão organizada para publicação.

### Mapa
* Mosaico de 7 imagens-base (OpenStreetMap) com regiões clicáveis em **2D** e **3D**.
* **154 quadras** do Plano Diretor com código novo e antigo, visíveis conforme o zoom e pesquisáveis.
* Bairros e localidades (Luzimangues e bairros, Taquaralto, Taquarussu, Capivara, Aureny, Jardim Taquari).
* Geometrias reais do OpenStreetMap: aeroporto, ATA, Agrotins, aterro, lago, estádio, rodoviária, Feira da 304 Sul,
  Terminal Multimodal, ferrovia Norte-Sul, rodovias (BR-010, TO-080, TO-030, TO-348, TO-455, TO-050), avenidas e 16 cursos d’água.
* 17 condomínios/residenciais nomeados e 23 áreas de lazer.

### Experiência turística
* 38 marcadores com ícones desenhados, em 7 temas com filtros: praias e lago, cultura e lazer, natureza, esportes,
  transporte, serviços e compras, placas de destino.
* Pontos incluídos: Ponte da Amizade, Palácio Araguaia, Praça dos Girassóis, Parque Cesamar, UFT, praias (Graciosa, Arnos,
  Prata, Caju), Ilha Canela, Lago de Palmas, Estádio, Kartódromo, Aeroporto, Rodoviária, Agrotins, Taquaruçu, Serra do Lajeado,
  Feira da 304 Sul, SESC, Palacinho da Cultura, SEBRAE-TO, CATUR (3 unidades), Palmas Shopping, Espaço Cultural, HGP, ULBRA,
  Católica do Tocantins e placas (Miracema, Lajeado, Paraíso, Porto Nacional, Taquaralto, Taquaruçu, Aureny’s, Praia dos Buritis).
* Banner, bússola, cartões de destaque e **tour guiado** (27 paradas) com transição zoom out → deslocar → zoom in.
* Busca (inclui quadras por código novo ou antigo), **menu retrátil** (computador e celular), temas claro e escuro.

### Modo 3D
* Câmera livre, atalhos de ângulo e vista “Turística”; áreas achatadas e translúcidas.
* Serra do Lajeado, sol e céu, água animada, barcos, parapentes, aviões, palmeiras e monumentos.

### Engenharia
* Gerador reproduzível (`src/build.py`), pipeline de dados numerado e verificado, testes automáticos e publicação via GitHub Pages.
* Documentação em `docs/`.
