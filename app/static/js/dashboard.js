document.addEventListener("DOMContentLoaded", () => {
  const priceCtx = document.getElementById('priceChart').getContext('2d');
  const anomCtx = document.getElementById('anomChart') ? document.getElementById('anomChart').getContext('2d') : null;
  const ticksTableBody = document.querySelector('#ticksTable tbody');
  const kpiPrice = document.getElementById('kpi-price');
  const kpiAnom = document.getElementById('kpi-anom');
  const kpiForecast = document.getElementById('kpi-forecast');
  const activityLog = document.getElementById('activityLog');

  let priceChart = new Chart(priceCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Price', data: [], borderColor:'#ff4b2b', backgroundColor:'rgba(255,75,43,0.08)', tension:0.2 }]},
    options: { responsive:true }
  });

  let anomChart = null;
  if (anomCtx) {
    anomChart = new Chart(anomCtx, {
      type: 'bar',
      data: { labels: ['anomalies'], datasets: [{ label:'Anomalies', data:[0], backgroundColor:'#1f6feb' }]},
      options: { responsive:true }
    });
  }

  async function refreshRealtime() {
    try {
      const res = await fetch('/api/realtime?n=200');
      const json = await res.json();
      const ticks = json.snapshot || [];
      ticksTableBody.innerHTML = '';
      ticks.slice().reverse().forEach(t => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${new Date(t.timestamp).toLocaleTimeString()}</td><td>${t.symbol}</td><td>${t.price}</td><td>${t.volume}</td>`;
        ticksTableBody.appendChild(tr);
      });
      if (ticks.length > 0) {
        const sym = ticks[ticks.length-1].symbol;
        const filtered = ticks.filter(x=>x.symbol===sym).slice(-100);
        priceChart.data.labels = filtered.map(f=>new Date(f.timestamp).toLocaleTimeString());
        priceChart.data.datasets[0].data = filtered.map(f=>f.price);
        priceChart.update();
        kpiPrice.textContent = filtered.length ? filtered[filtered.length-1].price : '--';
      }
      // anomaly batch
      const anomResp = await fetch('/api/detect-anomaly', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({})});
      const anomJson = await anomResp.json();
      const flags = anomJson.flags || anomJson.result || anomJson;
      const count = Array.isArray(flags) ? flags.length : (flags?.length || 0);
      kpiAnom.textContent = count;
      if (anomChart) {
        anomChart.data.datasets[0].data = [count];
        anomChart.update();
      }
      logActivity(`Refreshed: ${ticks.length} ticks, ${count} anomalies`);
    } catch (err) {
      logActivity("refresh error: " + err.message);
      console.error(err);
    }
  }

  document.getElementById('reloadBtn').addEventListener('click', refreshRealtime);

  document.getElementById('predictBtn').addEventListener('click', async () => {
    const val = document.getElementById('predictPrice').value.trim();
    if (!val) return alert('enter current_price or JSON window');
    let payload = {};
    try {
      if (val.startsWith('[')) payload.window = JSON.parse(val);
      else payload.current_price = parseFloat(val);
    } catch(e){ return alert('bad input'); }
    const r = await fetch('/api/predict-price', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    const j = await r.json(); document.getElementById('predictResult').textContent = 'Result: ' + JSON.stringify(j);
    kpiForecast.textContent = (j.prediction || j.predicted_price || '--');
    logActivity('Predict: ' + JSON.stringify(j));
  });

  document.getElementById('sentBtn').addEventListener('click', async () => {
    const text = document.getElementById('sentText').value.trim();
    if (!text) return alert('enter text');
    const r = await fetch('/api/sentiment', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text})});
    const j = await r.json();
    document.getElementById('sentResult').textContent = 'Sentiment: ' + JSON.stringify(j);
    logActivity('Sentiment: ' + JSON.stringify(j));
  });

  function logActivity(msg){
    const now = new Date().toLocaleTimeString();
    activityLog.textContent = `[${now}] ${msg}\n` + activityLog.textContent;
  }

  // auto refresh
  refreshRealtime();
  setInterval(refreshRealtime, 3000);
});
