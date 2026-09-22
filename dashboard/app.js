(function () {
  'use strict';
  const raw = window.FUNNEL_DATA;
  if (!Array.isArray(raw)) { document.body.innerHTML = '<p>Data file is missing. Keep dashboard/data.js beside dashboard/app.js.</p>'; return; }
  const $ = (id) => document.getElementById(id);
  const stages = ['impressions', 'clicks', 'leads', 'qualified_leads', 'customers'];
  const labels = ['Impressions', 'Clicks', 'Leads', 'Qualified', 'Customers'];
  const icons = ['◉', '➤', '▤', '♟', '✦'];
  const colors = ['#31bfff', '#37e4ee', '#b17bff', '#adf174', '#ff8390'];
  const channels = ['Paid Search', 'Organic Search', 'Paid Social', 'Email', 'Display'];
  const channelColors = {'Paid Search':'#34d5f5','Organic Search':'#ae82ff','Paid Social':'#fa73b6','Email':'#c4f077','Display':'#ff9c62'};
  const integer = new Intl.NumberFormat('en-US');
  const pct = (n, digits=1) => (Number.isFinite(n) ? n.toFixed(digits) : '0.0') + '%';
  const ratio = (a,b) => b ? 100*a/b : 0;
  const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const dates = {apr:'2024-04',mar:'2024-03',feb:'2024-02'};
  const prev = {apr:'2024-03',mar:'2024-02'};
  const fillSelect = (el, items) => { items.forEach(s => { const o = document.createElement('option'); o.value=s; o.textContent=s; el.appendChild(o); }); };
  fillSelect($('source'), channels);
  fillSelect($('device'), ['Desktop','Mobile','Tablet']);
  const sum = rows => rows.reduce((a,r) => { for (const k of stages) a[k] += Number(r[k]); a.spend_pkr += Number(r.spend_pkr); return a; }, {impressions:0,clicks:0,leads:0,qualified_leads:0,customers:0,spend_pkr:0});
  const selection = (month) => raw.filter(r => (!month || r.date.startsWith(month)) && ($('source').value === 'all' || r.source === $('source').value) && ($('device').value === 'all' || r.device === $('device').value));
  const delta = (current, previous, available) => available && previous ? (current / previous - 1) * 100 : null;
  const change = n => n === null ? 'Select a month to compare periods' : `${n >= 0 ? '▲ +' : '▼ '}${pct(n)} vs. previous month`;
  function renderKpis(now, before, comparative) {
    const items = [
      {name:'Impressions', value:integer.format(now.impressions), detail:change(delta(now.impressions,before.impressions,comparative)), icon:'◉'},
      {name:'Clicks', value:integer.format(now.clicks), detail:`${pct(ratio(now.clicks,now.impressions))} click-through · ${change(delta(now.clicks,before.clicks,comparative))}`, icon:'➤', cls:'cyan'},
      {name:'Qualified leads', value:integer.format(now.qualified_leads), detail:`${pct(ratio(now.qualified_leads,now.impressions),2)} of impressions · ${change(delta(now.qualified_leads,before.qualified_leads,comparative))}`, icon:'♟', cls:'purple'},
      {name:'Customers', value:integer.format(now.customers), detail:`${pct(ratio(now.customers,now.impressions),2)} of impressions · ${change(delta(now.customers,before.customers,comparative))}`, icon:'✦', cls:'green'}
    ];
    $('kpis').innerHTML = items.map(i => `<article class="kpi ${i.cls||''}"><span class="badge" aria-hidden="true">${i.icon}</span><div><strong>${i.value}</strong><div class="name">${i.name}</div><div class="detail">${esc(i.detail)}</div></div></article>`).join('');
  }
  function renderFunnel(now) {
    $('overall').textContent = pct(ratio(now.customers,now.impressions),2);
    $('funnel').innerHTML = stages.map((k,i) => {
      const left = i ? now[stages[i-1]] - now[k] : null;
      const drop = i && now[stages[i-1]] ? ratio(left,now[stages[i-1]]) : 0;
      return `<div class="stage" style="--accent:${colors[i]}"><span class="symbol" aria-hidden="true">${icons[i]}</span><span class="title">${labels[i]}</span><div class="count">${integer.format(now[k])}</div><div class="of">${pct(ratio(now[k],now.impressions),i===4?2:1)} of impressions</div>${i?`<div class="drop">↓ ${pct(drop,0)} <span>drop · ${integer.format(left)} lost</span></div>`:'<div class="drop" style="color:#aac4e7">Start of journey</div>'}</div>`;
    }).join('');
    const losses = stages.slice(1).map((k,i) => ({from:labels[i],to:labels[i+1],lost:now[stages[i]]-now[k], prior:now[stages[i]]}));
    const biggest = losses.reduce((a,b) => b.lost > a.lost ? b : a);
    $('leakPct').textContent = pct(ratio(biggest.lost,biggest.prior),0);
    $('leakDesc').innerHTML = `of <b>${esc(biggest.from.toLowerCase())}</b> drop before reaching <b>${esc(biggest.to.toLowerCase())}</b>.`;
    $('leakNum').textContent = `${integer.format(biggest.lost)} lost at ${biggest.from} → ${biggest.to} · largest count loss`;
    return biggest;
  }
  function renderChannels(rows) {
    const result = channels.map(s => ({name:s, ...sum(rows.filter(r => r.source===s))})).sort((a,b)=>b.customers-a.customers);
    const max = Math.max(1,...result.map(r=>r.customers));
    $('channelBody').innerHTML = result.map(r => `<tr><td><div class="channame"><span>${esc(r.name)}</span><span class="track"><i style="width:${100*r.customers/max}%;background:${channelColors[r.name]}"></i></span></div></td><td>${integer.format(r.customers)}</td><td class="rate">${pct(ratio(r.customers,r.impressions),2)}</td></tr>`).join('');
    return result;
  }
  function renderScatter(result) {
    const width=590,height=208,left=52,right=25,top=22,bottom=34;
    const maxI=Math.max(1,...result.map(r=>r.impressions))*1.16;
    const maxR=Math.max(.1,...result.map(r=>ratio(r.customers,r.impressions)))*1.22;
    const maxC=Math.max(1,...result.map(r=>r.customers));
    const plotW=width-left-right,plotH=height-top-bottom;
    let svg=`<svg viewBox="0 0 ${width} ${height}" aria-hidden="true"><g stroke="#3a416c" stroke-width="1">`;
    for(let i=0;i<=4;i++){const x=left+plotW*i/4,y=top+plotH*i/4;svg+=`<line x1="${x}" x2="${x}" y1="${top}" y2="${top+plotH}"/><line x1="${left}" x2="${left+plotW}" y1="${y}" y2="${y}"/>`;}
    svg+='</g><g fill="#aeb6d6" font-size="11" font-family="Arial">';
    for(let i=0;i<=4;i++){svg+=`<text x="${left+plotW*i/4}" y="${height-8}" text-anchor="middle">${Math.round(maxI*i/4/1000)}k</text><text x="${left-9}" y="${top+plotH*(4-i)/4+4}" text-anchor="end">${(maxR*i/4).toFixed(2)}%</text>`;}
    svg+='</g>';
    result.forEach((r) => { if(!r.impressions) return;const rate=ratio(r.customers,r.impressions),x=left+plotW*r.impressions/maxI,y=top+plotH*(1-rate/maxR),rad=7+15*Math.sqrt(r.customers/maxC);svg+=`<g><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${rad.toFixed(1)}" fill="${channelColors[r.name]}" fill-opacity=".82" stroke="#fff" stroke-opacity=".65"><title>${esc(r.name)}: ${integer.format(r.impressions)} impressions, ${integer.format(r.customers)} customers, ${pct(rate,2)}</title></circle><text x="${Math.min(width-66,x+rad+7).toFixed(1)}" y="${(y+4).toFixed(1)}" fill="#edf3ff" font-size="10" font-family="Arial">${esc(r.name)}</text></g>`;});
    $('scatter').innerHTML=svg+'</svg>';
    $('scatter').setAttribute('aria-label',result.map(r=>`${r.name}: ${integer.format(r.impressions)} impressions, ${integer.format(r.customers)} customers, ${pct(ratio(r.customers,r.impressions),2)} conversion`).join('; '));
  }
  function renderActions(loss, channelsSorted, now) {
    const bestRate = [...channelsSorted].filter(r=>r.impressions).sort((a,b)=>ratio(b.customers,b.impressions)-ratio(a.customers,a.impressions))[0];
    const targeted = loss.from==='Impressions' ? ['Test new ad creative and targeting','Compare click-through rate and eventual customers with a controlled experiment.'] : loss.from==='Clicks' ? ['Audit landing page and lead form','Test page speed, copy and form friction; assess qualified leads and customers.'] : ['Investigate '+loss.from.toLowerCase()+' handoff','Review qualification rules and follow-up time; measure customer outcomes.'];
    const steps=[targeted,['Compare source mix and lead quality',bestRate?`${bestRate.name} has the highest observed overall conversion (${pct(ratio(bestRate.customers,bestRate.impressions),2)}). Check scale and acquisition cost before reallocating.`:'Insufficient data in this selection for channel comparison.'],['Run a measurable follow-up test',`Current selection converts ${pct(ratio(now.customers,now.impressions),2)} of impressions. Set a customer conversion goal and compare like-for-like periods.`]];
    $('actions').innerHTML=steps.map((x,i)=>`<li><span class="stepnumber">${i+1}</span><span><b>${esc(x[0])}</b><small>${esc(x[1])}</small></span></li>`).join('');
  }
  function update(){
    const period=$('period').value;
    const rows=selection(dates[period]);
    const prior=prev[period]?selection(prev[period]):[];
    const now=sum(rows),before=sum(prior);
    renderKpis(now,before,Boolean(prev[period]));
    const biggest=renderFunnel(now);
    const ranked=renderChannels(rows);
    renderScatter(ranked);
    renderActions(biggest,ranked,now);
  }
  function download(){
    const rows=selection(dates[$('period').value]);
    const fields=['date','source','device','campaign','impressions','clicks','leads','qualified_leads','customers','spend_pkr'];
    const body=[fields.join(','),...rows.map(row=>fields.map(k=>`"${String(row[k]).replace(/"/g,'""')}"`).join(','))].join('\r\n');
    const objectUrl=URL.createObjectURL(new Blob(['\ufeff'+body],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=objectUrl;a.download=`future_ds_03_${$('period').value}_${$('source').value.replaceAll(' ','_')}_${$('device').value}.csv`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(objectUrl),60000);
  }
  for(const id of ['period','source','device']) $(id).addEventListener('change',update);
  $('export').addEventListener('click',download);
  update();
})();
