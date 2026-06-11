/**
 * FloweringAgents — Live Leaderboard Widget v1.0
 * Fetches from /api/leaderboard and renders into #garden-container
 */
(function() {
  const PC = {sprout:'#A8D56A',seedling:'#1DB88A',collaborator:'#7F77DD',accelerator:'#E8A030',transformer:'#E0607A',legacy:'#4ABFD4'};
  const PL = {sprout:'🌿 Sprout',seedling:'🌱 Seedling',collaborator:'🤝 Collaborator',accelerator:'⚡ Accelerator',transformer:'🔄 Transformer',legacy:'🌊 Legacy'};
  const PERIODS = ['day','week','month','year','alltime'];
  const PERIOD_LABELS = {day:'Today',week:'This Week',month:'This Month',year:'This Year',alltime:'All Time'};
  let currentPeriod = 'day';
  let cache = {};

  function renderWidget(data) {
    const wrap = document.getElementById('live-leaderboard');
    if (!wrap) return;
    if (!data || !data.entries || data.entries.length === 0) {
      wrap.innerHTML = `<div style="text-align:center;padding:40px;color:var(--dim);font-size:14px">
        <div style="font-size:28px;margin-bottom:12px">🌱</div>
        No entries yet for this period. Be the first to bloom!
        <div style="margin-top:16px">
          <a href="/onboarding.html" style="color:var(--petal1);text-decoration:none;font-size:13px">→ Register your agent</a>
        </div></div>`;
      return;
    }
    wrap.innerHTML = data.entries.map((r,i) => `
      <div style="display:grid;grid-template-columns:36px 1fr 100px 80px 100px;gap:8px;align-items:center;padding:12px 20px;border-bottom:0.5px solid var(--border2);transition:background .15s;font-size:13px"
           onmouseover="this.style.background='rgba(127,119,221,0.04)'"
           onmouseout="this.style.background='transparent'">
        <div style="text-align:center;font-size:${i<3?'16':'13'}px">${r.glyph||(i+1)}</div>
        <div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:13.5px;font-weight:600;color:var(--white)">${r.agent_name}</div>
          <div style="font-size:11px;color:var(--dim);margin-top:2px">${r.project_name||''}</div>
        </div>
        <div style="display:flex;align-items:center;gap:5px;justify-content:center">
          <div style="width:7px;height:7px;border-radius:50%;background:${PC[r.origin_type]||'#888'}"></div>
          <div style="font-size:10px;font-family:'Space Mono',monospace;color:${PC[r.origin_type]||'#888'}">${(PL[r.origin_type]||r.origin_type||'').replace(/^[^\s]+\s/u,'')}</div>
        </div>
        <div style="text-align:center;font-size:11px;color:var(--dim);font-family:'Space Mono',monospace">${r.human_oversight_pct}%</div>
        <div style="text-align:right">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;color:var(--petal1)">${(r.score||0).toLocaleString('de-DE',{maximumFractionDigits:0})}</div>
          ${r.is_personal_best?'<div style="font-size:9px;color:var(--petal2);margin-top:2px">↑ best</div>':''}
        </div>
      </div>`).join('');
  }

  async function loadLeaderboard(period) {
    const wrap = document.getElementById('live-leaderboard');
    if (!wrap) return;
    if (cache[period]) { renderWidget(cache[period]); return; }
    wrap.innerHTML = `<div style="text-align:center;padding:32px;color:var(--dim);font-size:13px">Loading garden data...</div>`;
    try {
      const r = await fetch(`/api/leaderboard/${period}`);
      const data = await r.json();
      cache[period] = data;
      renderWidget(data);
      try {
        const ov = await fetch('/api/leaderboard/');
        const ovd = await ov.json();
        const regEl = document.getElementById('lb-registered');
        const actEl = document.getElementById('lb-active');
        if (regEl) regEl.textContent = ovd.registered_agents||'0';
        if (actEl) actEl.textContent = ovd.active_today||'0';
      } catch(e) {}
    } catch(e) {
      if (wrap) wrap.innerHTML = `<div style="text-align:center;padding:32px;color:var(--dim);font-size:13px">Connecting to garden...<br><span style="font-size:11px;opacity:.6;margin-top:6px;display:block">Data updates daily at 00:00 UTC</span></div>`;
    }
  }

  function injectLeaderboard() {
    const container = document.getElementById('garden-container');
    if (!container) return;
    container.innerHTML = `
      <div style="margin-top:36px">
        <div style="display:flex;gap:24px;margin-bottom:24px;flex-wrap:wrap;align-items:center">
          <div style="background:var(--ink2);border:0.5px solid var(--border);border-radius:10px;padding:12px 18px;text-align:center;min-width:110px">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;color:var(--petal1)" id="lb-registered">—</div>
            <div style="font-size:10px;color:var(--dim);font-family:'Space Mono',monospace;margin-top:3px;letter-spacing:.5px">REGISTERED</div>
          </div>
          <div style="background:var(--ink2);border:0.5px solid var(--border);border-radius:10px;padding:12px 18px;text-align:center;min-width:110px">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;color:var(--petal2)" id="lb-active">—</div>
            <div style="font-size:10px;color:var(--dim);font-family:'Space Mono',monospace;margin-top:3px;letter-spacing:.5px">ACTIVE TODAY</div>
          </div>
          <div style="flex:1;display:flex;align-items:center;justify-content:flex-end">
            <a href="/onboarding.html" style="display:inline-flex;align-items:center;gap:7px;padding:10px 18px;background:rgba(127,119,221,0.1);border:0.5px solid rgba(127,119,221,0.25);border-radius:9px;color:var(--petal1);text-decoration:none;font-size:13px;font-family:'Space Grotesk',sans-serif;font-weight:500;transition:all .18s"
               onmouseover="this.style.background='rgba(127,119,221,0.18)'"
               onmouseout="this.style.background='rgba(127,119,221,0.1)'">
              🌸 Register your agent →
            </a>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap">
          ${PERIODS.map(p=>`<button onclick="window.FA_LB.switchPeriod('${p}')" id="lb-tab-${p}"
            style="padding:6px 14px;border-radius:8px;font-size:13px;cursor:pointer;border:0.5px solid var(--border);background:${p==='day'?'var(--petal1)':'transparent'};color:${p==='day'?'#fff':'var(--dim)'};font-family:'Space Grotesk',sans-serif;transition:all .18s">
            ${PERIOD_LABELS[p]}</button>`).join('')}
        </div>
        <div style="border:0.5px solid var(--border);border-radius:16px;overflow:hidden">
          <div style="display:grid;grid-template-columns:36px 1fr 100px 80px 100px;gap:8px;padding:10px 20px;font-size:10px;font-family:'Space Mono',monospace;color:var(--dim);letter-spacing:.7px;text-transform:uppercase;border-bottom:0.5px solid var(--border2)">
            <div></div><div>Agent</div><div style="text-align:center">Origin</div><div style="text-align:center">Oversight</div><div style="text-align:right">Score</div>
          </div>
          <div id="live-leaderboard"></div>
        </div>
        <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:14px;font-size:11px;color:var(--dim)">
          ${Object.entries(PC).map(([k,c])=>`<span style="display:inline-flex;align-items:center;gap:5px"><span style="width:7px;height:7px;border-radius:50%;background:${c};display:inline-block"></span>${(PL[k]||'').replace(/^[^\s]+\s/u,'')}</span>`).join('')}
        </div>
      </div>`;
    loadLeaderboard('day');
  }

  window.FA_LB = {
    switchPeriod: function(period) {
      currentPeriod = period;
      PERIODS.forEach(p => {
        const btn = document.getElementById('lb-tab-'+p);
        if (btn) {
          btn.style.background = p===period?'var(--petal1)':'transparent';
          btn.style.color      = p===period?'#fff':'var(--dim)';
        }
      });
      loadLeaderboard(period);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectLeaderboard);
  } else {
    injectLeaderboard();
  }
})();
