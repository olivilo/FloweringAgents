
/* ═══════════════════════════════════════════════════════════════
   BLOOM CANVAS v3
   - Multi-orbit: Ring 1 (bis 6), Ring 2 (bis 12), Ring 3 (bis 18)…
   - Gesamtstrauß skaliert nach außen mit mehr Agenten
   - Logo/Favicon in Blütenmitte, Fallback: Initialen
   - Lebendige HSL-Farben, harmonieren mit Logo
   - Skaliert bis zu hunderten ohne Performance-Probleme
═══════════════════════════════════════════════════════════════ */
(function(){
  var old = document.getElementById('bloomCanvas');
  if (!old) return;
  var c = document.createElement('canvas');
  old.replaceWith(c); c.id = 'bloomCanvas';

  var agents = [];
  var t = 0, started = false;

  /* Lebendige HSL-Farb-Palette */
  var HUES = [148, 262, 32, 345, 205, 82, 18, 290, 170, 55, 120, 220, 0, 300, 60];

  function agentColor(i) {
    return 'hsl(' + HUES[i % HUES.length] + ',62%,46%)';
  }
  function agentColorA(i, a) {
    return 'hsla(' + HUES[i % HUES.length] + ',62%,46%,' + a + ')';
  }

  function size() {
    var s = c.parentElement.clientWidth || 300;
    c.width = s*2; c.height = s*2;
    c.style.width = s+'px'; c.style.height = s+'px';
  }
  size(); window.addEventListener('resize', size);

  /* Initialen-Canvas Cache */
  var iCache = {};
  function initialsCanvas(name, hue, r) {
    var key = name + hue;
    if (iCache[key]) return iCache[key];
    var oc = document.createElement('canvas');
    oc.width = oc.height = Math.ceil(r*4);
    var x = oc.getContext('2d');
    x.fillStyle = 'hsl('+hue+',55%,42%)';
    x.beginPath(); x.arc(r*2,r*2,r*2,0,Math.PI*2); x.fill();
    var init = (name||'?').split(/[\s\-_]+/).slice(0,2).map(function(w){return (w[0]||'').toUpperCase();}).join('');
    x.fillStyle = '#fff';
    x.font = 'bold '+Math.round(r*1.3)+'px Inter,sans-serif';
    x.textAlign = 'center'; x.textBaseline = 'middle';
    x.fillText(init.slice(0,2), r*2, r*2);
    iCache[key] = oc;
    return oc;
  }

  /* ── Fraktale Orbit-Verteilung ──────────────────────────────────────────
     Statt starrem 6-12-18 Raster: organische Verteilung wie eine echte
     Blütenstruktur (Phyllotaxis-inspiriert). Ein zentraler Kern, dann
     wachsende Ringe mit ungeraden, natürlich wirkenden Kapazitäten.
     Bei 7 Agenten z.B.: 1 Mitte, 4 innerer Ring, 2 äußerer Ring.        */
  function buildOrbits(n) {
    if (n === 1) return [[0]];
    if (n === 2) return [[0,1]];

    var rings = [];
    var idx = 0;
    var remaining = n;

    /* Erster Ring: klein (3-5), je nach n */
    var firstRingSize = remaining <= 5 ? remaining : (remaining <= 9 ? 4 : 5);
    while (remaining > 0) {
      var capacity = rings.length === 0 ? firstRingSize : Math.round(firstRingSize * Math.pow(1.7, rings.length));
      var take = Math.min(capacity, remaining);
      var ring = [];
      for (var j = 0; j < take; j++) ring.push(idx++);
      rings.push(ring);
      remaining -= take;
    }
    return rings;
  }

  function drawFlower(ctx, x, y, r, hue, petalAngle, agIdx) {
    var ag = agents[agIdx] || {};

    /* Glow */
    var g = ctx.createRadialGradient(x,y,0,x,y,r*2.8);
    g.addColorStop(0, 'hsla('+hue+',62%,55%,0.20)');
    g.addColorStop(1, 'hsla('+hue+',62%,55%,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(x,y,r*2.8,0,Math.PI*2); ctx.fill();

    /* 6 petals — vibrant with highlight */
    for (var k = 0; k < 6; k++) {
      var pa = petalAngle + k * Math.PI/3;
      var px = x + Math.cos(pa) * r * 0.92;
      var py = y + Math.sin(pa) * r * 0.92;
      /* Main petal */
      ctx.beginPath();
      ctx.ellipse(px, py, r*0.56, r*0.29, pa, 0, Math.PI*2);
      ctx.fillStyle = 'hsla('+hue+',65%,50%,0.90)';
      ctx.fill();
      /* Highlight on petal */
      ctx.beginPath();
      ctx.ellipse(
        px - Math.cos(pa)*r*0.12,
        py - Math.sin(pa)*r*0.12,
        r*0.20, r*0.10, pa, 0, Math.PI*2
      );
      ctx.fillStyle = 'rgba(255,255,255,0.32)';
      ctx.fill();
    }

    /* Center white disc */
    var cr = r * 0.36;
    ctx.beginPath(); ctx.arc(x,y,cr,0,Math.PI*2);
    ctx.fillStyle = '#FDFAF5'; ctx.fill();
    /* Colored ring */
    ctx.beginPath(); ctx.arc(x,y,cr,0,Math.PI*2);
    ctx.strokeStyle = 'hsla('+hue+',55%,45%,0.55)';
    ctx.lineWidth = r*0.07; ctx.stroke();

    /* Logo or initials */
    var ir = cr * 0.86;
    var logo = ag.logoImg;
    ctx.save();
    ctx.beginPath(); ctx.arc(x,y,ir,0,Math.PI*2); ctx.clip();
    if (logo && logo.complete && logo.naturalWidth > 0) {
      ctx.drawImage(logo, x-ir, y-ir, ir*2, ir*2);
    } else {
      var ic = initialsCanvas(ag.name, hue, Math.max(4, Math.round(ir)));
      ctx.drawImage(ic, x-ir, y-ir, ir*2, ir*2);
    }
    ctx.restore();
  }

  function draw() {
    var ctx = c.getContext('2d');
    var W = c.width, H = c.height, cx = W/2, cy = H/2;
    ctx.clearRect(0,0,W,H);

    var n = Math.max(1, agents.length);
    var petal = t * 0.004;
    var orbitSpeed = t * 0.0012;

    if (n === 1) {
      drawFlower(ctx, cx, cy, W*0.15, HUES[0], petal, 0);
    } else {
      var rings = buildOrbits(n);
      var numRings = rings.length;
      /* Kamera-Zoom-Effekt: mit jeder weiteren Ring-Ebene zieht sich
         die Kamera zurück — ALLE Blüten werden gleichzeitig kleiner,
         damit weiterhin alle Ringe ins Bild passen. */
      var cameraZoom = Math.pow(0.74, numRings - 1);
      var maxOuterR = Math.min(W,H) * 0.46;
      var gIdx = 0;

      /* Ring-Radien zuerst berechnen */
      var ringRadii = [];
      for (var ri2 = 0; ri2 < numRings; ri2++) {
        var frac2 = numRings > 1 ? ri2 / (numRings - 1) : 0;
        ringRadii.push(maxOuterR * (0.22 + frac2 * 0.78) * cameraZoom + maxOuterR * (1 - cameraZoom) * 0.15);
      }

      /* EINHEITLICHE Blütengröße: vom Kamera-Zoom gewünscht,
         aber nie größer als der engste Ring erlaubt (keine Überlappung) */
      var desiredR = Math.max(5, W * 0.11 * cameraZoom);
      var tightestR = Infinity;
      rings.forEach(function(ring, ri) {
        var arcPerFlower = (2 * Math.PI * ringRadii[ri]) / ring.length;
        var maxRByArc = arcPerFlower / (1.48 * 2) * 0.62;
        tightestR = Math.min(tightestR, maxRByArc);
      });
      var flowerR = Math.max(3, Math.min(desiredR, tightestR));

      rings.forEach(function(ring, ri) {
        var ringR   = ringRadii[ri];
        var ringOff = orbitSpeed * (1 - ri * 0.20) + ri * 0.9;
        ring.forEach(function(agentOrigIdx, ji) {
          var a = ringOff + ji * 2*Math.PI / ring.length;
          var x = cx + ringR * Math.cos(a);
          var y = cy + ringR * Math.sin(a);
          var hue = HUES[gIdx % HUES.length];
          drawFlower(ctx, x, y, flowerR, hue, petal + gIdx*0.75, gIdx);
          gIdx++;
        });
      });
    }
    t++; requestAnimationFrame(draw);
  }

  function start() { if (!started) { started = true; draw(); } }

  /* Load agents list for logos + count */
  fetch('/api/agents/')
    .then(function(r){ return r.json(); })
    .then(function(d){
      var list = (d.agents || []).slice(0, 200); /* cap at 200 for perf */
      agents = list.map(function(a, i) {
        var ag = { name: a.agent_name || '?', logoImg: null };
        if (a.website_url) {
          try {
            var domain = new URL(a.website_url).hostname;
            var img = new Image();
            /* Eigener Backend-Proxy statt direkt Google — cached serverseitig,
               robuster gegen Drittanbieter-Ausfälle/Rate-Limits */
            img.src = '/api/favicons/' + domain + '.png';
            img.onload = function(){ ag.logoImg = img; };
          } catch(e) {}
        }
        return ag;
      });
      var el = document.getElementById('bloom-count');
      if (el) el.textContent = agents.length;
      start();
    })
    .catch(function(){
      agents = [{name:'?'}];
      start();
    });

  setTimeout(start, 1500);
})();

/* ── DIARY SNIPPET ── */
fetch('/api/stories/latest')
  .then(function(r){ return r.json(); })
  .then(function(d){
    var text = d.content_en || d.content_de || '';
    if (text.length > 200) text = text.substring(0,197) + '…';
    if (text) { var el = document.getElementById('diary-snippet'); if(el) el.textContent = text; }
  }).catch(function(){});
