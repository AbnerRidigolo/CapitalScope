# CapitalScope

BI local para explorar fundos brasileiros com **dados públicos reais da CVM**. A primeira versão acompanha Fundos de Investimento em Participações (FIP) e Fundos de Investimento em Direitos Creditórios (FIDC).

## Abrir em dois passos

Requer Python 3.10+; não exige banco, credenciais ou serviço cloud.

```bash
git clone https://github.com/AbnerRidigolo/CapitalScope.git
cd CapitalScope
python -m http.server 8082 --bind 127.0.0.1 --directory app/dist
```

Abra http://127.0.0.1:8082. O diretório `app/dist` contém a versão compilada e seu snapshot JSON. Sirva o diretório completo; não abra apenas o HTML via `file://`.

## O que está pronto

- Visão de mercado com patrimônio reportado e comparação da mesma base de CNPJs entre competências.
- Busca de fundos/classes por nome ou CNPJ e ficha com histórico.
- Universos FIP e FIDC separados, filtros de competência e qualidade.
- Cenários explicitamente hipotéticos sobre os dados reais.
- Fontes inspecionáveis, regras de cálculo, manifestos SHA256 e auditoria de exclusões.

**Cobertura desta extração:** 23.318 posições, em 30/04/2025, 31/08/2025, 31/12/2025 e 30/04/2026. Na última posição: 2.103 FIPs e 4.235 FIDCs após tratamento. Extração em 18/09/2026. As competências foram escolhidas para alinhar os universos; não constituem os dados mais recentes disponíveis.

## Fontes reais e escopo

- [CVM — FIP quadrimestral](https://dados.cvm.gov.br/dataset/fip-doc-inf_quadrimestral).
- [CVM — FIDC mensal](https://dados.cvm.gov.br/dataset/fidc-doc-inf_mensal).

A base FIP **não fornece uma classificação confiável e pronta de VC, Growth e PE**. Essa classificação requer curadoria de documentos das gestoras e não foi inventada. FIDCs representam um recorte de crédito estruturado, não todo Private Credit. O painel não contém carteira de uma gestora, receita/EBITDA de investidas, cap tables ou rodadas.

Variação do patrimônio não é rentabilidade. Não calculamos TIR, TVPI ou múltiplos sem os fluxos necessários. Investimentos cruzados entre fundos podem duplicar exposição econômica nos agregados. Nulos não são convertidos em observações de zero; PL negativo é preservado.

## Atualizar e testar

```bash
python scripts/ingest_cvm.py --refresh
node --test tests/metrics.test.mjs
python -m unittest discover -s tests -p "test_*.py"
```

Sem `--refresh`, a ingestão reutiliza arquivos em `data/raw`. O snapshot normalizado é salvo em `app/src/data.json`; **é necessário recompilar para atualizar `app/dist`**. Os arquivos de origem são públicos e não ficam versionados; URLs e hashes ficam em `data/manifest.json`.

O frontend usa React, JavaScript e CSS sobre o runtime Data App. O build desta entrega usou o compilador local do plugin Data, com verificação das fronteiras do runtime. Em um ambiente Node compatível com Vite 8, o projeto também fornece o fluxo de build de fonte:

```bash
cd app
npm ci
npm run build
```

Esse segundo fluxo não foi executado nesta entrega. Instruções do runtime em `app/AGENTS.md`. Não há implantação em AWS, Databricks ou Azure ML nesta versão.

## Estrutura

- `scripts/ingest_cvm.py`: coleta e normalização com a biblioteca padrão do Python.
- `app/src/content/dashboard/`: interface e cálculos do CapitalScope.
- `app/src/data.json`: snapshot público normalizado e proveniência.
- `data/`: manifestos, cobertura e exclusões.
- `tests/`: reconciliação, filtros, granularidade e cenários.
- `docs/methodology.md`: definições e decisões.
- `docs/linkedin.md`: texto da publicação.

Dados CVM sob [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Atribuição e condições em `DATA_LICENSE.md`. Os dados derivados mantêm essa licença. Não representa recomendação de investimento nem produto oficial da CVM.
