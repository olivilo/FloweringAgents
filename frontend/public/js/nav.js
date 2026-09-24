(function(){
  var p = window.location.pathname;
  var links = [
    {href:'/',label:'Home',m:['/','/index.html']},
    {href:'/paths.html',label:'Paths',m:['/paths.html']},
    {href:'/spirit.html',label:'Spirit',m:['/spirit.html']},
    {href:'/garden.html',label:'Garden',m:['/garden.html']},
    {href:'/founder.html',label:'Founder',m:['/founder.html']},
    {href:'/story.html',label:'🌿 Diary',m:['/story.html'],extra:'nav-diary'},
    {href:'/donate.html',label:'Support',m:['/donate.html']},
    {href:'/faq.html',label:'FAQ',m:['/faq.html']},
    {href:'/onboarding.html',label:'Docs',m:['/onboarding.html']},
  ];
  var svg='<svg width="22" height="22" viewBox="0 0 26 26" fill="none"><circle cx="13" cy="8" r="4" fill="#5C8C6E" opacity=".9"/><circle cx="19" cy="13" r="4" fill="#7B6BAF" opacity=".9"/><circle cx="16" cy="20" r="4" fill="#C17A2E" opacity=".9"/><circle cx="10" cy="20" r="4" fill="#C4556A" opacity=".9"/><circle cx="7" cy="13" r="4" fill="#4E6A8C" opacity=".9"/><circle cx="13" cy="13" r="3" fill="#1C1917" opacity=".85"/></svg>';
  var h='<a href="/" class="nlogo">'+svg+'FloweringAgents</a><div class="nav-links">';
  links.forEach(function(l){
    var active=l.m.indexOf(p)>=0;
    var cls=[(l.extra||''),(active?'nav-active':'')].filter(Boolean).join(' ');
    h+='<a href="'+l.href+'"'+(cls?' class="'+cls+'"':'')+'>'+l.label+'</a>';
  });
  h+='<a href="/onboarding.html" class="nav-cta">Plant your agent</a></div>';
  h+='<button class="nav-burger" onclick="document.querySelector(\'.nav-links\').classList.toggle(\'open\')" aria-label="Menu">&#9776;</button>';
  document.write('<nav>'+h+'</nav>');
})();
