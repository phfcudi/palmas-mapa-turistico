# Limitações conhecidas

Este documento existe para evitar que o mapa seja lido como mais preciso do que é.

## Precisão geográfica
* Os contornos de **bairros e localidades** (Luzimangues e seus bairros, Taquaralto, Taquarussu, Capivara, Aureny, Jardim Taquari)
  foram **desenhados à mão** sobre as imagens: não são divisas oficiais. O OpenStreetMap não tem polígonos desses locais.
* As **quadras** têm posição aproximada (erro típico de até meia quadra, ~180 m na comparação com as alamedas do OSM).
  Foram incluídas 154; faltam as que o esquema não permitiu isolar (por exemplo 612 N, 512 N, 406 N, 105 S, 107 S, 108 S, 109 S
  e as faixas 401–602 N) e algumas do extremo sul.
* **Posições aproximadas** (estimadas pela ilustração do mapa turístico ou por manchas de areia do mapa-base):
  SESC, Palacinho da Cultura, CATUR (as 3 unidades), Palmas Shopping, SEBRAE-TO, Espaço Cultural, HGP, Católica do Tocantins,
  Praia da Graciosa, Praia das Arnos, Praia do Caju, Ilha Canela e as placas de destino. **A Serra do Lajeado e o Mirante da
  Serra são ilustrativos** (ficam fora das imagens).
* Com apoio de dados do OSM: Feira da 304 Sul (polígono real), ULBRA (vias “Ulbra – Entrada Aeroporto”), Praia do Prata,
  Agrotins, Aeroporto, ATA, Estádio Nilton Santos, Rodoviária, Kartódromo.
* A **Praia dos Buritis** aparece só como placa de estrada (como no mapa turístico); a praia fica fora das imagens.
* Frigovale e Prata têm contorno à mão; a ferrovia e o terminal usam geometria do OSM.

## Conteúdo
* Textos vêm de fontes citadas em cada ficha; **horários, telefones e endereços mudam** — confirme em canais oficiais antes de divulgar.
* O endereço do CATUR central vem de uma captura do Google Maps; as unidades do aeroporto e de Taquaruçu têm fonte parcial
  (reportagem e resumo não oficial). Sem a confirmação do portal da Prefeitura (que bloqueia leitura automática).
* O código **antigo** de algumas quadras difere entre fontes (ex.: 110 S = ARSE 14 pela regra, ARSE 15 no PDF). A regra de numeração foi adotada.

## Técnicas
* **O modo 3D foi validado apenas por simulação de código** no ambiente de desenvolvimento (sem GPU/rede para carregar o Three.js).
  O modo 3D foi validado visualmente em [GOOGLE CHROME, MICROSOFT EDGE, SMARTPHONE SAMSUNG ANDROID, GOOGLE CHROME, NAVEGADOR SAMSUNG]. Verifique: serra, água, barcos, parapentes,
  aviões, palmeiras, monumentos e a vista “Turística”.
* O 3D e a fonte dependem de CDNs (cdnjs e Google Fonts). Sem internet o 2D funciona; o 3D mostra um aviso.
* Celulares simples podem ficar lentos com a **Animação** ligada; há um botão para desligá-la.
* As imagens-base são rasterizadas (~1 340 px de largura cada): em zoom muito alto ficam serrilhadas.
* O mapa não tem navegação por rotas nem localização do usuário.
* Os dados do OSM são de uma data específica; vias e polígonos novos não aparecem sem refazer a exportação.
