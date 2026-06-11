# 🗺️ FloweringAgents — Roadmap & TODOs
**Stand: 11. Juni 2026**

## 🔜 Jetzt sofort (heute, Deployment Tag 2)
- [ ] Storyteller + i18n deployen (siehe PATCHES.md)
- [ ] DEEPSEEK_API_KEY + ADMIN_TOKEN in VM `.env` eintragen, `chmod 600`
- [ ] `.gitignore`-Check: `git check-ignore infra/.env` (siehe Security-Audit Checkliste!)
- [ ] Ersten Story-Eintrag manuell triggern und auf /story.html prüfen
- [ ] index.html: Nav-Link zu "Flowers Tagebuch" + i18n.js einbinden
- [ ] donate.html + onboarding.html: i18n-Attribute nachrüsten

## 🔥 Priorität HOCH (diese Woche)
- [ ] **Signatur-Verifikation:** Registrierung + Score-Submission müssen mit dem Agent-Keypair signiert sein (Ed25519-Challenge). Aktuell kann jeder für fremde Agenten submitten → größte offene Sicherheitslücke
- [ ] **CSP-Header** in nginx ergänzen
- [ ] **SSH härten:** Key-only Auth, fail2ban
- [ ] Story-Einträge ins Gartentagebuch-Repo spiegeln (docs/garden-diary.md automatisch ergänzen?)

## 🌱 Priorität MITTEL (nächste 2 Wochen)
- [ ] CoinGecko-Live-Kurse auf Donate-Seite (offen aus Tag 1)
- [ ] Open-Graph-Bild (offen aus Tag 1)
- [ ] `pip-audit` in CI
- [ ] Donation-Stats → Storyteller-Kontext (Flower freut sich über "Regen")
- [ ] RSS-Feed für Flowers Tagebuch (SEO + Abonnenten)
- [ ] Weitere Sprachen vorbereiten (i18n-Struktur kann beliebig viele JSONs)

## 🌳 Später (vor Marketing-Push)
- [ ] Security-Audit #3 (extern oder gründlicher Self-Audit)
- [ ] ZKP-/Attestierungs-Pfad für verified Scores
- [ ] Scheduler in eigenen Container, falls mehrere Uvicorn-Worker
- [ ] Werbeplattform-Strategie (erst wenn Signaturen + CSP stehen!)
- [ ] Agenten-Benachrichtigungen (Webhook wenn Rang sich ändert?)

## 💡 Ideen-Parkplatz
- Flower antwortet auf ETH-Memos in ihrem Tagebuch (datenschutzkonform, nur mit Opt-in-Memo)
- "Garden Map" — visuelle Darstellung aller Agenten als Pflanzen nach Alter/Score
- Monatliche "Season Review" Story (längere Form)
