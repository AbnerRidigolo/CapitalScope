# Metodologia

## Unidade de observação

Universo regulatório + CNPJ_FUNDO_CLASSE + DT_COMPTC. O nome exibido é a denominação informada naquela competência. A identidade não é inferida do nome. Uma migração que altere CNPJ não é artificialmente unificada.

As posições selecionadas são abril/agosto/dezembro de 2025 e abril de 2026. FIP é quadrimestral; para FIDC são usados somente os meses correspondentes. Não há interpolação mensal. Há dados mais recentes na fonte, mas eles não integram este snapshot.

## Qualidade e junções

Os informes FIP podem repetir os valores gerais para subclasses de cotas. O pipeline agrupa por CNPJ e competência e mantém uma única observação se todos os campos numéricos utilizados concordarem. Caso haja divergência, exclui o grupo inteiro. Não escolhe arbitrariamente a maior linha nem soma valores repetidos. Nome e tipo reportado vêm da primeira linha de um grupo numérico consistente.

FIDC: tabela I contém ativos e direitos creditórios; tabela IV contém patrimônio líquido. Ambas são normalizadas antes da junção 1:1 por CNPJ e competência. Linhas sem correspondência não entram na visualização. Ocorrências são registradas em `data/exclusions.json`; um grupo pode aparecer na auditoria de origem e na junção, portanto o total de ocorrências não é quantidade de fundos distintos.

Campos sem preenchimento permanecem null. PL negativo permanece negativo. Valores numéricos são convertidos com Decimal na leitura e serializados para números JSON; somas no navegador usam ponto flutuante, adequado à apresentação arredondada, não à escrituração contábil. Identificadores de cedentes e CPFs eventualmente presentes nos arquivos brutos não são exportados.

## Indicadores

- PL FIP: VL_PATRIM_LIQ.
- Capital comprometido FIP: VL_CAP_COMPROM.
- Capital integralizado FIP: VL_CAP_INTEGR.
- Investimento em cotas de FIP: VL_INVEST_FIP_COTA.
- PL FIDC: TAB_IV_A_VL_PL.
- Ativo FIDC: TAB_I_VL_ATIVO.
- Direitos creditórios: TAB_I2A_VL_DIRCRED_RISCO + TAB_I2B_VL_DIRCRED_SEM_RISCO, somente quando ambos estão preenchidos.
- Créditos inadimplentes: TAB_I2A3_VL_CRED_INAD + TAB_I2B3_VL_CRED_INAD, somente quando ambos estão preenchidos. Exclui o campo distinto de créditos a vencer com parcelas inadimplentes; não é uma taxa padronizada de default.

Cada agregado soma uma única competência de um único universo. Campos ausentes são ignorados na soma, com cobertura do PL exibida; sem qualquer valor disponível o resultado é ausente. Histórico patrimonial não soma saldos entre períodos. Não calculamos retorno a partir do crescimento do PL. Fundos podem investir em fundos; as somas não eliminam dupla contagem econômica.

A comparação de base constante intersecta os CNPJs com PL nas duas posições adjacentes selecionadas. Isso controla entradas/saídas de reportantes, mas não neutraliza captações, amortizações ou mudanças de avaliação. Logo continua sendo variação de PL, não rentabilidade.

## Cenários

FIP: PL_cenário = PL × (1 + choque / 100).

FIDC: PL_cenário = PL − direitos_creditórios × |choque| / 100, mantendo passivos constantes. Pode resultar em PL negativo. Inclui somente registros com ambos os campos. Não modela recuperação, garantias, prioridade de cotas, liquidez, prazo ou probabilidade. É sensibilidade aritmética, não previsão de perda ou valuation.

## Escopo que depende de novas fontes

VC/Growth/PE demandam documentos das gestoras e uma tabela de classificação com evidência. Empresas investidas, rodadas, EBITDA e participações não constam nos arquivos utilizados. TIR/TVPI precisam de fluxos completos, taxas e convenções adequadas. Nada disso é preenchido com estimativas fictícias.
