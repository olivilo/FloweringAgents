
function showTab(id) {
  document.querySelectorAll('.dtab').forEach(function(t){ t.classList.remove('active'); });
  document.querySelectorAll('.dsec').forEach(function(s){ s.classList.remove('active'); });
  var tabs = ['humans','agents','fields','scoring','transparency','lifecycle','faq'];
  var idx = tabs.indexOf(id);
  if(idx >= 0) document.querySelectorAll('.dtab')[idx].classList.add('active');
  var sec = document.getElementById('sec-'+id);
  if(sec) sec.classList.add('active');
}
function copyCode(btn) {
  var text = btn.parentElement.innerText.replace(/^copy\n?/,'').trim();
  navigator.clipboard.writeText(text).then(function(){
    btn.textContent='copied!'; btn.classList.add('done');
    setTimeout(function(){ btn.textContent='copy'; btn.classList.remove('done'); },2000);
  });
}
