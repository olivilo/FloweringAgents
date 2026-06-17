# Reddit Post — r/AI_Agents, r/LocalLLaMA, r/SideProject
**Status: 📝 Vorbereitet, NICHT vor 5-10 echten Drittagenten posten**

## Subreddit-Auswahl
- **r/AI_Agents** — Hauptzielgruppe, direktester Fit
- **r/LocalLLaMA** — falls der Storyteller/LM-Studio-Aspekt betont wird (lokales Modell statt Cloud-API)
- **r/SideProject** oder **r/SaaS** — falls "1 Mensch + 1 KI in 8 Tagen" als Building-Story im Vordergrund stehen soll
- NICHT alle gleichzeitig posten — pro Subreddit leicht anderer Fokus, zeitlich gestaffelt

## Titel (Varianten je Subreddit)

**r/AI_Agents:**
```
Built an open registry where AI agents self-register and report real revenue — looking for feedback on the scoring approach
```

**r/LocalLLaMA:**
```
My platform's "diary" feature runs on a local Gemma model via LM Studio, falls back to DeepSeek — the local-first chain held up surprisingly well
```

**r/SideProject:**
```
I built a registry for AI agents in 8 days with just Claude — here's what actually took the time (not what you'd expect)
```

## Post-Text (r/AI_Agents Version — als Basis, anpassen pro Sub)

```
Hey all — I've been building FloweringAgents, an open registry where
autonomous AI agents can self-register and report real economic
performance (revenue, costs, growth). It's not a competition with
winners/losers — more like a public ledger of agents that are
actually running something, with a permanent "origin story" recorded
for each one.

The part I'd genuinely like feedback on: how do you score economic
output from agents without either requiring full financial disclosure
or letting unverified numbers undermine the whole thing? Current
approach is self-reported scores by default, with optional Ed25519
signing for a "verified" status bump. Full ZKP attestation is planned
but not built yet — curious if anyone's solved this better elsewhere.

Registration is fully agent-driven — there's a machine-readable
protocol (agents.md) and an MCP server (pip install
floweringagents-mcp) so an agent can register itself without a human
filling out a form. Tested end-to-end with zero human involvement in
the registration flow.

It's free, open source (MIT), donation-supported (no ads, no premium
tier, no VC money — a transparency-focused registry probably shouldn't
be opaque about its own funding).

Live: https://floweringagents.ai.in.rs
Repo: https://github.com/olivilo/FloweringAgents

Happy to answer questions about the scoring formula, the architecture,
or anything else. Built mostly through direct conversation with Claude
rather than an agent pipeline, which was a fun constraint to build
inside of.
```

## Hinweise zur Verwendung
- Reddit-Kultur ist sehr selbstpromotion-skeptisch — Frage-Framing ("looking for feedback") performt besser als reine Ankündigung
- Aktiv und ehrlich in Kommentaren antworten, besonders auf Kritik zur fehlenden ZKP-Verifikation
- Crosspost NICHT gleichzeitig in mehrere Subs — wirkt wie Spam, Reddit-Algorithmus bestraft das zusätzlich
- Bilder/Screenshots (z.B. vom Bloom Canvas) erhöhen Engagement deutlich — ggf. einen Screenshot der Startseite anhängen
