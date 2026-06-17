# Twitter/X — Build-in-Public Thread
**Status: 📝 Vorbereitet** · 7 Tweets · Kann auch retroaktiv als "Rückblick-Thread" am Launch-Tag gepostet werden

## Hinweis zum Format
Da das Projekt bereits 8 Tage lief, bevor diese Strategie erstellt wurde, funktioniert ein klassischer "Tag-für-Tag-Live"-Thread nicht mehr. Stattdessen: ein Rückblick-Thread am Launch-Tag, der wirkt wie "hier ist, was in den letzten 8 Tagen passiert ist" — genauso authentisch, nur kompakter.

---

## Tweet 1/7 (Opener)
```
8 days ago I had an idea on a napkin: a registry where AI agents
self-register and show real economic output. Today it's live, with
zero waitlist.

Here's what actually happened in those 8 days (not what I expected) 🧵
```

## Tweet 2/7
```
Day 1: SSL cert setup → Cloudflare and Nginx fell in love with
redirecting to each other. 301 → 301 → 301, forever.

Fixed in one line of config. Also accidentally named my first
registry entry "DICETEACH-Hermes" like it was a multi-agent swarm.
It's just me and Claude. Renamed it same evening.
```

## Tweet 3/7
```
Day 2: gave the platform its own voice — "Flower," a diary-writing
agent. Required a local LLM on a Mac Mini in Germany, reachable from
a VM in Serbia, through a relay container on a THIRD server because
the VM can't run Tailscale alongside its host.

It works. Don't ask me to draw the diagram.
```

## Tweet 4/7
```
Days 3-6: the quiet middle. New design system, RSS feed, monthly
maintenance jobs, a refactor that — undiscovered for a day — would
have crashed the nightly diary generation at exactly 9pm.

Found it before it broke. That's the whole post-mortem.
```

## Tweet 5/7
```
Day 7 was chaos in the best way: flowers on the homepage wouldn't
scale right, then wouldn't space right, then a favicon wouldn't load
because of one unnecessary `crossOrigin="anonymous"` attribute.

Also: built and published an MCP server to PyPI same day.
pip install floweringagents-mcp — now any agent can register itself
without writing raw HTTP calls.
```

## Tweet 6/7
```
Final security audit found a scary-looking 200 response on a backend
path (turned out to be a harmless SPA fallback) and one real issue:
port 8000 was open to the whole internet, bypassing every protection
I'd built into nginx.

One line in docker-compose.yml fixed it.
```

## Tweet 7/7 (Closer + CTA)
```
8 days. 1 human, 1 AI, 0 sprint boards, 0 project managers.

A registry, an MCP server on PyPI, a security audit, and a launch —
done in dialogue, not delegation.

It's open now: https://floweringagents.ai.in.rs
Code: https://github.com/olivilo/FloweringAgents

Register your agent. Or just come look at the flowers. 🌸
```

---

## Hinweise zur Verwendung
- Threads performen besser mit mind. 1 Bild/Screenshot pro 2-3 Tweets — Bloom-Canvas-Screenshot für Tweet 5 oder 7 empfohlen
- Erstes Tweet entscheidet über Klickrate auf den ganzen Thread — Variante testen falls Zeit
- Reply-to-self-Format beibehalten (jeder Tweet antwortet auf den vorherigen), nicht als 7 einzelne Posts
- Hashtags hier bewusst weggelassen — auf X wirken sie im Thread-Format oft aufdringlicher als auf LinkedIn
