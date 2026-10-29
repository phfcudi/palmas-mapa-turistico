# pipeline/

Scripts de preparação de dados, numerados na ordem de execução. Cada script lê e grava em `data/processed/`
(`os.chdir(PROC)` no início) e usa `src/paths.py` para localizar as entradas.

Veja a tabela completa, os requisitos e a explicação de cada passo em **[../docs/PIPELINE_DE_DADOS.md](../docs/PIPELINE_DE_DADOS.md)**.

```bash
pip install -r requirements-pipeline.txt     # na raiz do repositório
python pipeline/03_refs_quadras_osm.py
python pipeline/04_calibrar_osm.py
python pipeline/05_refinar_quadras.py
python pipeline/06_osm_para_regioes.py
python pipeline/07_osm_regioes_extra.py
```

Notas:
* Windows: defina `PYTHONUTF8=1` (os arquivos são UTF-8).
* Os scripts 01 e 02 exigem o GIF de terceiros (`data/external/`) e o programa `tesseract`; os resultados deles já estão versionados.
* Alguns scripts salvam imagens de conferência (`ov_*.png`) em `data/processed/`; elas são ignoradas pelo Git.
* Estes scripts nasceram como ferramentas de pesquisa: priorizam o resultado reproduzível sobre a elegância do código.
