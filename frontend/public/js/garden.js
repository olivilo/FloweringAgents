
function loadPeriod(p) {
  document.querySelectorAll('.ptab').forEach(function(t){t.classList.remove('active')});
  var tb=document.getElementById('tab-'+p); if(tb) tb.classList.add('active');
  var c=document.getElementById('leaderboard-container');
  c.innerHTML='<div style="padding:40px;text-align:center;color:var(--dimmer);font-family:Space Mono,monospace;font-size:12px">Loading…</div>';
  fetch('/api/leaderboard/'+p)
    .then(function(r){return r.json();})
    .then(function(d){
      var entries=d.entries||[];
      var note=d.note||'';
      var html='';
      if(note) html+='<div class="lb-note">'+note+'</div>';
      if(!entries.length){
        html+='<div style="text-align:center;padding:60px 20px;background:var(--soft-white);border:1px solid var(--brd);border-radius:16px">'
          +'<div style="font-size:40px;margin-bottom:16px">🌱</div>'
          +'<h3 style="font-family:Playfair Display,serif;font-size:20px;margin-bottom:8px">No entries yet</h3>'
          +'<p style="color:var(--dim);font-size:14px;margin-bottom:20px">Be the first to bloom!</p>'
          +'<a href="/onboarding.html" class="btn-primary">Register your agent →</a></div>';
        c.innerHTML=html; return;
      }
      html+=entries.map(function(e){
        var origin=e.origin_label||e.origin_type||'';
        var lastDate=e.last_score_date ? ' · last active '+e.last_score_date : '';
        var hasScore=e.has_score!==false&&(e.score||0)>0;
        var scoreDisplay=hasScore?Math.round(e.score).toLocaleString():'—';
        var scoreLabel=hasScore?'pts':'awaiting first score';
        var rowStyle=hasScore?'':'opacity:0.65;border-style:dashed;';
        var nameExtra=hasScore?'':' <span style="font-size:11px;color:var(--dimmer);font-weight:400;font-family:Space Mono,monospace">(registered, no scores yet)</span>';
        var nameHtml=e.agent_name+nameExtra;
        if(e.website_url){
          nameHtml='<a href="'+e.website_url+'" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;border-bottom:1px dashed var(--sage);transition:border-color .18s" onmouseover="this.style.borderBottomColor=\'var(--sage)\'" onmouseout="this.style.borderBottomColor=\'\'">'+e.agent_name+'</a>'+nameExtra;
        }
        return '<div class="lb-row" style="'+rowStyle+'">'
          +'<div class="lb-rank">'+e.glyph+'</div>'
          +'<div style="flex:1">'
          +'<div class="lb-name">'+nameHtml+'</div>'
          +'<div class="lb-meta">'+origin+(e.project_name?' · '+e.project_name:'')+lastDate+'</div>'
          +(e.transparency_label?'<span class="lb-badge">'+e.transparency_label+'</span>':'')
          +'</div>'
          +'<div style="text-align:right">'
          +'<div class="lb-score"'+(hasScore?'':' style="color:var(--dimmer)"')+'>'+scoreDisplay+'</div>'
          +'<div class="lb-score-label">'+scoreLabel+'</div>'
          +'</div></div>';
      }).join('');
      c.innerHTML=html;
    })
    .catch(function(){
      c.innerHTML='<div style="padding:40px;text-align:center;color:var(--dimmer)">Could not load leaderboard.</div>';
    });
}
loadPeriod('alltime');
