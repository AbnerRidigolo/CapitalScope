Quero construir minha carreira no mercado financeiro. Para aproximar meus projetos desse objetivo, comecei o CapitalScope: um BI local para explorar fundos brasileiros com dados públicos reais da CVM.

A primeira versão reúne FIPs e FIDCs, com busca por fundo ou CNPJ, histórico patrimonial, comparação de uma mesma base de fundos entre períodos e cenários de sensibilidade.

O desafio mais interessante apareceu antes dos gráficos: definir corretamente a unidade de análise. Nos informes de FIP, valores gerais podem se repetir em linhas de subclasses. Somar tudo diretamente distorceria os indicadores.

Por isso, implementei regras para consolidar repetições consistentes, excluir conflitos, preservar valores ausentes e registrar a origem dos arquivos com hashes SHA256. O projeto também tem testes de reconciliação, filtros e cenários.

Nesta extração, são 23.318 posições de fundos/classes, distribuídas em quatro competências entre abril de 2025 e abril de 2026.

Uma decisão importante foi respeitar os limites da fonte: variação de patrimônio não é rentabilidade; FIPs não são classificados automaticamente como VC, Growth ou PE; e as simulações aparecem separadas dos valores reportados.

Meu objetivo é desenvolver a capacidade de conectar engenharia de dados, análise e perguntas relevantes para o mercado financeiro.

Código e documentação: https://github.com/AbnerRidigolo/CapitalScope

#Dados #BusinessIntelligence #Python #MercadoFinanceiro #FundosDeInvestimento #EngenhariaDeDados #Portfolio
