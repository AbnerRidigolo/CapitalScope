export const sum=(rows,key)=>rows.reduce((n,r)=>n+(r[key]??0),0);
export function total(rows,key){const present=rows.filter(r=>r[key]!==null&&r[key]!==undefined);return present.length?sum(present,key):null;}
export function aggregate(rows){return {nav:total(rows,'nav'),paid:total(rows,'paid'),committed:total(rows,'committed'),receivables:total(rows,'receivables'),overdue:total(rows,'overdue'),count:rows.length,covered:rows.filter(r=>r.nav!==null).length};}
export function scope(rows,filters={}){const u=['FIP','FIDC'].includes(filters.universe)?filters.universe:'FIP';return rows.filter(r=>r.universe===u&&(!filters.coverage||filters.coverage==='all'||r.coverage===filters.coverage));}
export function series(rows){return [...new Set(rows.map(r=>r.date))].sort().map(date=>({date,...aggregate(rows.filter(r=>r.date===date))}));}
export function pairedChange(rows,previous){const old=new Map(previous.filter(r=>r.nav!==null).map(r=>[r.id,r]));const comparable=rows.filter(r=>r.nav!==null&&old.has(r.id));return {count:comparable.length,before:sum(comparable.map(r=>old.get(r.id)),'nav'),after:sum(comparable,'nav')};}
export function scenario(rows,shock){return rows.map(r=>({...r,scenarioNav:r.nav===null?null:r.universe==='FIP'?r.nav*(1+shock/100):r.receivables===null?null:r.nav-r.receivables*Math.abs(shock)/100}));}
export const money=n=>n===null||n===undefined?'Não informado':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',notation:'compact',maximumFractionDigits:1}).format(n);
export const exact=n=>n===null||n===undefined?'Não informado':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(n);
export const num=n=>new Intl.NumberFormat('pt-BR').format(n);
export const dateLabel=d=>new Date(d+'T12:00:00').toLocaleDateString('pt-BR');
