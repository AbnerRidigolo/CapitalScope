# Verificação da primeira versão com dados reais

Data: 18/09/2026.

- 7 testes JavaScript: granularidade/CNPJ, recortes, nulos, saldos no tempo, base comparável, cenários e reconciliação com o relatório de ingestão.
- 3 testes Python: consolidação de subclasses, exclusão de valores conflitantes e preservação de nulos/negativos.
- Build local do runtime Data App concluído com verificação de integridade.
- Extração com URLs e SHA256 em `data/manifest.json`; cobertura em `data/quality.json` e ocorrências em `data/exclusions.json`.

A compilação via `npm ci` / `npm run build` não foi executada. Não houve implantação cloud, execução em Databricks ou validação como sistema contábil. O snapshot é estático e não atualiza sozinho.
- Navegador: cinco páginas verificadas; troca FIP/FIDC; seleção de competência; busca por CNPJ; abertura de ficha; histórico; cenário e reset para diferença zero. Console sem erros.
- Inspeção visual em viewport desktop; mobile não inspecionado visualmente.
