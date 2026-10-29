# Como contribuir

Obrigado por ajudar a melhorar o mapa de Palmas!

## Reportar um erro de dados (o mais útil)
Abra uma *issue* informando:
* **Qual local** (nome e `id`, que aparece no endereço ao abrir a ficha: `#id`);
* **O que está errado** (posição, nome, código da quadra, texto);
* **A correção** — de preferência com **coordenadas** (clique com o botão direito no Google Maps/OSM e copie lat, lon),
  endereço oficial ou link de fonte confiável;
* Capturas de tela, se ajudarem.

Dados do **OpenStreetMap** (ruas, polígonos, nomes) também podem ser corrigidos direto em https://www.openstreetmap.org —
a correção melhora o mapa de todo mundo e entra aqui na próxima atualização dos dados.

## Enviar código ou dados
1. Faça um *fork* e crie uma branch (`feature/nome-curto` ou `fix/nome-curto`).
2. Rode `python src/build.py` e `pytest` (deve passar).
3. Abra o `dist/index.html` e confira visualmente a mudança (2D, 3D e celular, quando aplicável).
4. Atualize a documentação em `docs/` e o `CHANGELOG.md`.
5. Abra o *pull request* explicando **o que mudou e por quê**, e a **fonte** de qualquer dado novo.

## Regras
* **Não** inclua fotos, logotipos ou textos copiados de terceiros sem autorização (veja `docs/FONTES_E_LICENCAS.md`).
* Mantenha a atribuição ao OpenStreetMap.
* Marque no texto da ficha quando uma posição for **aproximada** e cite a fonte.
* Não edite `data/processed/*.json` à mão; mude os scripts ou os dados brutos e regenere.
* Mensagens de commit curtas e no imperativo, em português (ex.: `Adiciona ponto turístico Praça X`).
