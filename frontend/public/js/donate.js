
function copyAddr(id, btn) {
  var txt = document.getElementById(id).textContent.trim();
  navigator.clipboard.writeText(txt).then(function(){
    btn.textContent = '✓ Copied!';
    btn.classList.add('copied');
    setTimeout(function(){ btn.textContent = '📋 Copy address'; btn.classList.remove('copied'); }, 2000);
  });
}

// Load donation stats
fetch('/api/donations/stats')
  .then(function(r){ return r.json(); })
  .then(function(d){
    if (d.total_usd_est !== undefined) document.getElementById('stat-total').textContent = '$' + (d.total_usd_est||0).toFixed(2);
    if (d.unique_donors !== undefined) document.getElementById('stat-donors').textContent = d.unique_donors || 0;
    if (d.last_donation) document.getElementById('stat-last').textContent = new Date(d.last_donation).toLocaleDateString('en-GB');
    if (d.eth_received !== undefined) document.getElementById('eth-received').textContent = parseFloat(d.eth_received||0).toFixed(4) + ' ETH';
    if (d.trx_received !== undefined) document.getElementById('trx-received').textContent = parseFloat(d.trx_received||0).toFixed(2) + ' TRX';
    if (d.doge_received !== undefined) document.getElementById('doge-received').textContent = parseFloat(d.doge_received||0).toFixed(2) + ' DOGE';
  }).catch(function(){});
