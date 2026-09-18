"""Download and normalize public CVM data. No synthetic financial records."""
import argparse,csv,hashlib,io,json,urllib.request,zipfile
from collections import defaultdict
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw'
DATES=['2025-04-30','2025-08-31','2025-12-31','2026-04-30']
BASE='https://dados.cvm.gov.br/dados/'
URLS=[BASE+f'FIP/DOC/INF_QUADRIMESTRAL/DADOS/inf_quadrimestral_fip_{y}.csv' for y in [2025,2026]]+[BASE+f'FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_{d[:7].replace("-","")}.zip' for d in DATES]
URLS += [BASE+'FIP/DOC/INF_QUADRIMESTRAL/META/meta_inf_quadrimestral_fip.txt',BASE+'FIDC/DOC/INF_MENSAL/META/meta_inf_mensal_fidc_txt.zip']
def number(v):
 return None if v is None or not v.strip() else float(Decimal(v))
def read_csv(b):return list(csv.DictReader(io.StringIO(b.decode('latin1')),delimiter=';'))
def key(r):return (r['CNPJ_FUNDO_CLASSE'],r['DT_COMPTC'])
def normalize(raw,mapping,universe,audit):
 groups=defaultdict(list)
 for r in raw:
  if r['DT_COMPTC'] in DATES: groups[key(r)].append(r)
 out={}
 for k,group in groups.items():
  conflicts=[field for field in mapping if len({number(r.get(field)) for r in group})>1]
  if conflicts:
   audit.append(dict(universe=universe,id=k[0],date=k[1],reason='conflicting_values',fields=conflicts,sourceRows=len(group)));continue
  r=group[0]
  out[k]=dict(id=k[0],date=k[1],name=r['DENOM_SOCIAL'],universe=universe,reportingType=r['TP_FUNDO_CLASSE'],sourceRows=len(group),**{target:number(r.get(field)) for field,target in mapping.items()})
 return out

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args();RAW.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for url in URLS:
  path=RAW/url.rsplit('/',1)[-1]
  if args.refresh or not path.exists():
   with urllib.request.urlopen(url,timeout=90) as response:payload=response.read()
   path.write_bytes(payload)
  payload=path.read_bytes();manifest.append(dict(url=url,file=path.name,sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload)))
 audit=[];raw_fip=[];raw_fidc=[];raw_pl=[]
 for y in [2025,2026]:raw_fip+=read_csv((RAW/f'inf_quadrimestral_fip_{y}.csv').read_bytes())
 for d in DATES:
  month=d[:7].replace('-','');z=zipfile.ZipFile(RAW/f'inf_mensal_fidc_{month}.zip')
  raw_fidc+=read_csv(z.read(f'inf_mensal_fidc_tab_I_{month}.csv'));raw_pl+=read_csv(z.read(f'inf_mensal_fidc_tab_IV_{month}.csv'))
 fip=normalize(raw_fip,{'VL_PATRIM_LIQ':'nav','VL_CAP_COMPROM':'committed','VL_CAP_INTEGR':'paid','VL_INVEST_FIP_COTA':'fundHoldings'},'FIP',audit)
 credit=normalize(raw_fidc,{'TAB_I_VL_ATIVO':'assets','TAB_I2A_VL_DIRCRED_RISCO':'creditWithRisk','TAB_I2B_VL_DIRCRED_SEM_RISCO':'creditWithoutRisk','TAB_I2A3_VL_CRED_INAD':'overdueWithRisk','TAB_I2B3_VL_CRED_INAD':'overdueWithoutRisk'},'FIDC-I',audit)
 pl=normalize(raw_pl,{'TAB_IV_A_VL_PL':'nav'},'FIDC-IV',audit)
 rows=[]
 for k,r in fip.items():
  r.update(admin=None,assets=None,receivables=None,overdue=None,coverage='PL ausente' if r['nav'] is None else 'PL negativo' if r['nav']<0 else 'Disponível');rows.append(r)
 admins={key(r):r['ADMIN'] for r in raw_fidc}
 for k,r in credit.items():
  if k not in pl:
   audit.append(dict(universe='FIDC',id=k[0],date=k[1],reason='missing_or_conflicting_PL_join'));continue
  def add(a,b):return None if r[a] is None or r[b] is None else r[a]+r[b]
  r.update(universe='FIDC',nav=pl[k]['nav'],committed=None,paid=None,fundHoldings=None,admin=admins[k],receivables=add('creditWithRisk','creditWithoutRisk'),overdue=add('overdueWithRisk','overdueWithoutRisk'))
  r['coverage']='PL ausente' if r['nav'] is None else 'PL negativo' if r['nav']<0 else 'Disponível';rows.append(r)
 rows.sort(key=lambda r:(r['date'],r['universe'],r['id']))
 assert len({(r['universe'],r['id'],r['date']) for r in rows})==len(rows)
 extracted=datetime.now(timezone.utc).isoformat()
 source=dict(type='public',name='CVM — informes de FIP e FIDC',description='Dados regulatórios públicos, sem registros sintéticos. ODbL 1.0. Posições selecionadas; não é uma carteira de uma gestora nem censo integral após exclusões.',executedAt=extracted,links=[{'label':'FIP quadrimestral','url':'https://dados.cvm.gov.br/dataset/fip-doc-inf_quadrimestral'},{'label':'FIDC mensal','url':'https://dados.cvm.gov.br/dataset/fidc-doc-inf_mensal'}],metricDefinitions=[{'label':'Patrimônio líquido','definition':'FIP: VL_PATRIM_LIQ; FIDC: TAB_IV_A_VL_PL. Somar somente dentro do universo e da mesma competência. Não representa retorno ou capital disponível; participações cruzadas podem gerar dupla contagem econômica.'},{'label':'Créditos inadimplentes','definition':'TAB_I2A3_VL_CRED_INAD + TAB_I2B3_VL_CRED_INAD. Não inclui os créditos a vencer com parcelas inadimplentes; não é uma taxa padronizada de default.'},{'label':'Capital integralizado','definition':'VL_CAP_INTEGR reportado por FIP, sem derivar retorno a partir do PL.'}],evidenceFlow=[{'title':'Download público CVM','detail':'URLs e SHA256 em data/manifest.json'},{'title':'Normalização e qualidade','detail':'python scripts/ingest_cvm.py; chave universo + CNPJ + competência. Linhas de subclasses colapsadas apenas se os valores utilizados concordarem; conflitos excluídos e registrados.'}])
 existing=json.loads((ROOT/'app/src/data.json').read_text(encoding='utf-8'))
 snapshot=dict(id=existing['id'],surface='dashboard',title='CapitalScope',status='reviewed',buildStatus='updating',generatedAt=extracted,filters=[dict(id='universe',label='Universo',field='universe',defaultValue='FIP',queryIds=['portfolio']),dict(id='coverage',label='Qualidade do PL',field='coverage',defaultValue='all',queryIds=['portfolio']),dict(id='asOf',label='Competência',field='date',defaultValue='2026-04-30',queryIds=['portfolio'])],queries={'portfolio':{'rows':rows,'source':source},'quality':{'rows':audit,'source':source}})
 summary=dict(extractedAt=extracted,dates=DATES,rawFipRows=len(raw_fip),rawFidcRows=len(raw_fidc),accepted=len(rows),excludedGroups=len(audit),positions=[dict(date=d,universe=u,entities=sum(r['date']==d and r['universe']==u for r in rows),nav=sum(r['nav'] or 0 for r in rows if r['date']==d and r['universe']==u)) for d in DATES for u in ['FIP','FIDC']])
 for path,data in [(ROOT/'app/src/data.json',snapshot),(ROOT/'data/manifest.json',dict(extractedAt=extracted,files=manifest)),(ROOT/'data/quality.json',summary),(ROOT/'data/exclusions.json',audit)]:path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
