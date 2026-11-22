"""Create an offline, filterable HTML dashboard from cleaned synthetic data.
Run: python scripts/build_dashboard.py
"""
from pathlib import Path
import json
import pandas as pd
from plotly.offline import get_plotlyjs

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data'/'processed'
OUT = ROOT/'dashboard.html'


def main():
    sales = pd.read_csv(DATA/'sales_enriched.csv')
    inv = pd.read_csv(DATA/'inventory.csv')
    products = pd.read_csv(DATA/'products.csv')
    regions = pd.read_csv(DATA/'regions.csv')
    inv = inv.merge(products[['product_id','product_name','therapy_area','reorder_level_units']],on='product_id')
    inv = inv.merge(regions[['region_id','region_name']],on='region_id')
    targets = pd.read_csv(DATA/'targets.csv')
    reps = pd.read_csv(DATA/'reps.csv')
    targets = targets.merge(reps[['rep_id','rep_name','region_id']],on='rep_id')
    targets = targets.merge(regions[['region_id','region_name']],on='region_id')
    visits = pd.read_csv(DATA/'visits.csv').merge(reps[['rep_id','rep_name','region_id']],on='rep_id')
    visits = visits.merge(regions[['region_id','region_name']],on='region_id')
    cols = ['month','region_name','rep_name','product_name','therapy_area','units_sold','returned_units','net_units','net_sales_inr','transaction_id']
    payload = {
        'sales': sales[cols].to_dict(orient='records'),
        'targets': targets[['month','region_name','rep_name','target_inr']].to_dict(orient='records'),
        'visits': visits[['month','region_name','rep_name','planned_visits','completed_visits']].to_dict(orient='records'),
        'inventory': inv[['month','region_name','product_name','therapy_area','stock_units','reorder_level_units']].to_dict(orient='records'),
    }
    payload_json = json.dumps(payload, separators=(',',':')).replace('</', '<\\/')
    plotly_js = get_plotlyjs()
    html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>PharmaPulse | Commercial Analytics Demo</title>
<style>
:root{--bg:#091322;--panel:#101f32;--panel2:#12243a;--line:#243a51;--text:#e9f0f8;--muted:#90a4bb;--teal:#45dbc6;--blue:#74a9ff;--amber:#ffc17a;--pink:#f092b6}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 15% 0%,#173551 0%,transparent 35%),var(--bg);font-family:Inter,system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:var(--text)}
.page{max-width:1450px;margin:0 auto;padding:30px 28px 70px}.top{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px}.brand{display:flex;align-items:center;gap:12px}.logo{width:48px;height:48px;border-radius:13px;background:linear-gradient(135deg,var(--teal),var(--blue));display:grid;place-items:center;color:#062130;font-size:29px;font-weight:800}.tiny{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--teal);font-weight:800}.top h1{margin:3px 0;font-size:29px;letter-spacing:-.7px}.muted{color:var(--muted)}.subtitle{font-size:13px;margin:6px 0 0}.demo{font-size:12px;color:var(--amber);padding:10px 15px;border:1px solid #7b5939;background:#352b27;border-radius:30px;font-weight:650}
.hero{margin-top:28px;padding:23px 25px;border:1px solid var(--line);border-radius:20px;background:linear-gradient(120deg,#122c41,#132138 65%,#172943)}.hero h2{font-size:21px;letter-spacing:-.3px;margin:0 0 8px}.hero p{color:#aac3d9;max-width:780px;font-size:13px;line-height:1.6;margin:0}.filters{display:flex;flex-wrap:wrap;gap:12px;margin-top:19px}.control{display:flex;flex-direction:column;gap:6px;font-size:11px;color:#9eb1c8;text-transform:uppercase;letter-spacing:.09em;font-weight:700}.control select{background:#0b1a2c;color:white;border:1px solid #345069;border-radius:9px;padding:10px 34px 10px 12px;min-width:170px;outline:0;font-size:13px;text-transform:none;letter-spacing:0}.export{align-self:end;background:var(--teal);border:0;color:#072834;font-weight:800;padding:11px 17px;border-radius:9px;cursor:pointer}.export:hover{filter:brightness(1.12)}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:22px}.kpi,.panel{background:var(--panel);border:1px solid var(--line);border-radius:17px}.kpi{padding:20px 20px 18px}.kpi .name{font-size:12px;color:#aabacf;font-weight:600}.kpi .value{font-size:30px;font-weight:800;letter-spacing:-.9px;margin:10px 0 5px}.kpi .note{color:#8ca5bb;font-size:11px}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px;background:var(--teal)}
.sectiontitle{display:flex;align-items:center;justify-content:space-between;margin:32px 1px 12px}.sectiontitle h3{margin:0;font-size:18px;letter-spacing:-.2px}.sectiontitle span{font-size:12px;color:#91a8be}.grid{display:grid;grid-template-columns:1.65fr 1fr;gap:14px}.grid.equal{grid-template-columns:1fr 1fr}.panel{padding:18px 16px}.panel h4{font-size:13px;margin:2px 5px 4px;font-weight:750;color:#e7f3ff}.panel p{font-size:11px;color:#90a7bf;margin:0 5px}.plot{height:325px}.lower{margin-top:14px}.tablewrap{max-height:398px;overflow:auto;margin:16px 3px 0}table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;color:#92aac3;font-size:11px;text-transform:uppercase;letter-spacing:.05em;padding:11px 10px;border-bottom:1px solid #2a3e55;position:sticky;top:0;background:var(--panel)}td{padding:11px 10px;border-bottom:1px solid #1d3248}td.num{text-align:right;font-variant-numeric:tabular-nums}th.num{text-align:right}.good{color:#56dfc2}.warn{color:#fbc17d}.footer{color:#89a2b9;font-size:12px;line-height:1.8;margin-top:28px}.footer strong{color:#bdd4e4}
@media(max-width:1050px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.grid,.grid.equal{grid-template-columns:1fr}}
@media(max-width:580px){.page{padding:18px 12px 50px}.top h1{font-size:22px}.hero{padding:17px}.kpis{gap:9px}.kpi{padding:15px}.kpi .value{font-size:23px}.control select{min-width:135px}.demo{font-size:10px}.panel{padding:12px 8px}.plot{height:290px}}
</style>
<script>__PLOTLY_JS__</script>
</head>
<body><main class="page">
<header class="top"><div class="brand"><div class="logo">P</div><div><div class="tiny">Commercial Intelligence / Portfolio Project</div><h1>PharmaPulse Analytics</h1><div class="subtitle muted">Sales • Field force • Product performance • Inventory health</div></div></div><span class="demo">● SYNTHETIC DEMONSTRATION DATA</span></header>
<section class="hero"><h2>Business performance at a glance</h2><p>Explore fictional pharmaceutical operations across five Indian sales regions. Filter revenue and product trends, compare teams against their targets, and review inventory reorder alerts. All calculations update locally in your browser.</p>
<div class="filters"><label class="control">Reporting period<select id="period"><option value="2026">2026 Jan–Oct</option><option value="2025">2025 Jan–Dec</option><option value="all">All 22 months</option></select></label><label class="control">Sales region<select id="region"><option value="all">All regions</option></select></label><label class="control">Therapy area<select id="therapy"><option value="all">All therapy areas</option></select></label><button class="export" id="export">↓ Export filtered sales CSV</button></div></section>
<section class="kpis"><article class="kpi"><div class="name"><span class="dot"></span>Net revenue</div><div class="value" id="kRevenue">—</div><div class="note" id="kRevenueSub">Net of discounts and returns</div></article><article class="kpi"><div class="name"><span class="dot" style="background:var(--blue)"></span>Net units sold</div><div class="value" id="kUnits">—</div><div class="note">Units excluding returned units</div></article><article class="kpi"><div class="name"><span class="dot" style="background:var(--pink)"></span>Unit return rate</div><div class="value" id="kReturn">—</div><div class="note">Returned units / gross units</div></article><article class="kpi"><div class="name"><span class="dot" style="background:var(--amber)"></span>Sales target attainment</div><div class="value" id="kTarget">—</div><div class="note" id="kTargetSub">Actual revenue / assigned targets</div></article></section>
<div class="sectiontitle"><h3>Revenue & market performance</h3><span id="dataCount"></span></div>
<div class="grid"><div class="panel"><h4>Monthly revenue trend</h4><p>₹ net sales, after discount and returns</p><div class="plot" id="trend"></div></div><div class="panel"><h4>Regional contribution</h4><p>Net revenue by sales region</p><div class="plot" id="regions"></div></div></div>
<div class="grid equal lower"><div class="panel"><h4>Top products</h4><p>Top eight fictional products by revenue</p><div class="plot" id="products"></div></div><div class="panel"><h4>Therapy area mix</h4><p>Revenue contribution by portfolio category</p><div class="plot" id="mix"></div></div></div>
<div class="sectiontitle"><h3>Field operations & inventory</h3><span>Current inventory snapshots: October 2026</span></div>
<div class="grid equal"><div class="panel"><h4>Sales executive performance</h4><p>Revenue, assigned sales goal, and customer visit completion</p><div class="tablewrap"><table><thead><tr><th>Executive</th><th class="num">Revenue</th><th class="num">Target %</th><th class="num">Visits %</th></tr></thead><tbody id="repTable"></tbody></table></div></div><div class="panel"><h4>Low-stock inventory alerts</h4><p>October 2026 • stock below fictional reorder thresholds</p><div class="tablewrap"><table><thead><tr><th>Product</th><th>Region</th><th class="num">Available</th><th class="num">Below by</th></tr></thead><tbody id="inventoryTable"></tbody></table></div></div></div>
<p class="footer"><strong>Important:</strong> This is a learning and portfolio demonstration, not an official Alteus Biogenics dashboard. Product names, employees, prices, targets, field visits and sales figures are entirely fictional. “Net revenue” means (units sold − units returned) × unit price × (1 − discount). Targets and field visits are not therapy-specific, so attainment is hidden when a single therapy area is selected. Source files, SQL queries and refresh scripts are included in this project.</p>
</main>
<script>
const DATA=__DASHBOARD_JSON__;
const C={teal:'#45dbc6',blue:'#74a9ff',amber:'#ffc17a',pink:'#f092b6',text:'#d9e8f5',muted:'#8da5be',line:'#304257'};
const compact=(n)=>{if(!Number.isFinite(n))return '—';let a=Math.abs(n);if(a>=1e7)return '₹'+(n/1e7).toFixed(2)+' Cr';if(a>=1e5)return '₹'+(n/1e5).toFixed(2)+' L';if(a>=1e3)return '₹'+(n/1e3).toFixed(1)+' K';return '₹'+Math.round(n).toLocaleString('en-IN')};
const int=(n)=>Math.round(n).toLocaleString('en-IN');
const pc=(a,b)=>b>0?(100*a/b).toFixed(1)+'%':'—';
const group=(rows,key,value)=>{const m=new Map();for(const r of rows)m.set(r[key],(m.get(r[key])||0)+Number(r[value]||0));return [...m].sort((a,b)=>b[1]-a[1])};
const isPeriod=m=>document.getElementById('period').value==='all'||m.slice(0,4)===document.getElementById('period').value;
const chartBase={paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{color:C.muted,size:11,family:'Inter, system-ui, sans-serif'},margin:{l:70,r:18,t:18,b:55},showlegend:false,hoverlabel:{bgcolor:'#1c3045',font:{color:'#fff'}},xaxis:{gridcolor:C.line,zeroline:false},yaxis:{gridcolor:C.line,zeroline:false}};
const pconf={responsive:true,displayModeBar:false};
const selects=(id,values)=>{let el=document.getElementById(id);for(let v of values.sort()){let o=document.createElement('option');o.value=v;o.textContent=v;el.append(o)}};
selects('region',[...new Set(DATA.sales.map(x=>x.region_name))]);selects('therapy',[...new Set(DATA.sales.map(x=>x.therapy_area))]);
let current=[];
function render(){
 const region=document.getElementById('region').value,therapy=document.getElementById('therapy').value;
 current=DATA.sales.filter(r=>isPeriod(r.month)&&(region==='all'||r.region_name===region)&&(therapy==='all'||r.therapy_area===therapy));
 const revenue=current.reduce((a,r)=>a+r.net_sales_inr,0), units=current.reduce((a,r)=>a+r.net_units,0),returns=current.reduce((a,r)=>a+r.returned_units,0),gross=current.reduce((a,r)=>a+r.units_sold,0);
 const targets=DATA.targets.filter(r=>isPeriod(r.month)&&(region==='all'||r.region_name===region));
 let targetTotal=targets.reduce((a,r)=>a+r.target_inr,0);
 document.getElementById('kRevenue').textContent=compact(revenue);
 document.getElementById('kUnits').textContent=int(units);
 document.getElementById('kReturn').textContent=pc(returns,gross);
 document.getElementById('kTarget').textContent=therapy==='all'?pc(revenue,targetTotal):'N/A';
 document.getElementById('kTargetSub').textContent=therapy==='all'?'Actual revenue / assigned targets':'Targets are not therapy-specific';
 document.getElementById('dataCount').textContent=int(current.length)+' sales transactions';
 const trend=group(current,'month','net_sales_inr').sort((a,b)=>a[0].localeCompare(b[0]));
 Plotly.react('trend',[{x:trend.map(x=>x[0]),y:trend.map(x=>x[1]),type:'scatter',mode:'lines+markers',fill:'tozeroy',line:{color:C.teal,width:3,shape:'spline'},marker:{size:7,color:C.teal},fillcolor:'rgba(69,219,198,.10)',hovertemplate:'%{x}<br>₹%{y:,.0f}<extra></extra>'}],{...chartBase,xaxis:{...chartBase.xaxis,type:'category',tickangle:-35},yaxis:{...chartBase.yaxis,tickprefix:'₹',tickformat:'~s'}},pconf);
 const regions=group(current,'region_name','net_sales_inr');
 Plotly.react('regions',[{type:'bar',x:regions.map(x=>x[1]),y:regions.map(x=>x[0]),orientation:'h',marker:{color:[C.teal,C.blue,'#72b7ed','#ba93ed',C.amber],line:{width:0}},hovertemplate:'%{y}: ₹%{x:,.0f}<extra></extra>'}],{...chartBase,margin:{l:82,r:17,t:18,b:50},yaxis:{...chartBase.yaxis,autorange:'reversed'},xaxis:{...chartBase.xaxis,tickprefix:'₹',tickformat:'~s'}},pconf);
 const prods=group(current,'product_name','net_sales_inr').slice(0,8);
 Plotly.react('products',[{type:'bar',x:prods.map(x=>x[1]).reverse(),y:prods.map(x=>x[0]).reverse(),orientation:'h',marker:{color:C.blue},hovertemplate:'%{y}: ₹%{x:,.0f}<extra></extra>'}],{...chartBase,margin:{l:105,r:19,t:18,b:50},xaxis:{...chartBase.xaxis,tickprefix:'₹',tickformat:'~s'}},pconf);
 const mix=group(current,'therapy_area','net_sales_inr');
 Plotly.react('mix',[{type:'pie',labels:mix.map(x=>x[0]),values:mix.map(x=>x[1]),hole:.68,textinfo:'percent',textposition:'outside',automargin:true,marker:{colors:[C.teal,C.blue,C.amber,C.pink,'#b193ed','#83c8e9']},hovertemplate:'%{label}<br>₹%{value:,.0f}<br>%{percent}<extra></extra>'}],{...chartBase,margin:{l:10,r:10,t:0,b:15},showlegend:true,legend:{orientation:'h',x:.5,xanchor:'center',y:-.10,font:{size:10}}},pconf);
 const byRep=group(current,'rep_name','net_sales_inr');
 const targetByRep=new Map(group(targets,'rep_name','target_inr'));
 const visits=DATA.visits.filter(r=>isPeriod(r.month)&&(region==='all'||r.region_name===region));
 let visitsByRep=new Map();for(let v of visits){let a=visitsByRep.get(v.rep_name)||[0,0];a[0]+=v.completed_visits;a[1]+=v.planned_visits;visitsByRep.set(v.rep_name,a)}
 document.getElementById('repTable').innerHTML=byRep.map(([name,rev])=>{let t=targetByRep.get(name)||0,vs=visitsByRep.get(name)||[0,0],ratio=t?rev/t:0;return `<tr><td>${name}</td><td class="num">${compact(rev)}</td><td class="num ${ratio>=1?'good':'warn'}">${therapy==='all'?pc(rev,t):'N/A'}</td><td class="num">${pc(vs[0],vs[1])}</td></tr>`}).join('')||'<tr><td colspan="4">No sales records for these filters.</td></tr>';
 let inventory=DATA.inventory.filter(r=>r.month==='2026-10'&&(region==='all'||r.region_name===region)&&(therapy==='all'||r.therapy_area===therapy)&&r.stock_units<r.reorder_level_units).sort((a,b)=>(b.reorder_level_units-b.stock_units)-(a.reorder_level_units-a.stock_units));
 document.getElementById('inventoryTable').innerHTML=inventory.map(i=>`<tr><td>${i.product_name}</td><td>${i.region_name}</td><td class="num">${int(i.stock_units)}</td><td class="num warn">${int(i.reorder_level_units-i.stock_units)}</td></tr>`).join('')||'<tr><td colspan="4">No low-stock alerts for this selection.</td></tr>';
}
for(let id of ['period','region','therapy'])document.getElementById(id).addEventListener('change',render);
document.getElementById('export').addEventListener('click',()=>{
 let cols=['transaction_id','month','region_name','rep_name','product_name','therapy_area','units_sold','returned_units','net_units','net_sales_inr'];
 let text=cols.join(',')+'\n'+current.map(r=>cols.map(c=>String(r[c]).includes(',')?'"'+String(r[c]).replaceAll('"','""')+'"':r[c]).join(',')).join('\n');
 let url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));let a=document.createElement('a');a.href=url;a.download='filtered_pharma_sales.csv';document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
});
render();
</script></body></html>'''
    html = html.replace('__PLOTLY_JS__', plotly_js).replace('__DASHBOARD_JSON__', payload_json)
    OUT.write_text(html, encoding='utf-8')
    print(f'Created offline dashboard: {OUT} ({OUT.stat().st_size/1e6:.2f} MB)')

if __name__ == '__main__':
    main()
