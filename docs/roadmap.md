# 🗺️ FloweringAgents — Roadmap & TODOs
**Stand: 14. Juni 2026 (Tag 4)**

## ✅ Erledigt in Tag 4

### Sicherheit
- [x] **CSP-Header** in nginx — Content-Security-Policy mit self + Google Fonts + cdnjs
- [x] **CSS-Ordner** in nginx location blocks ergänzt

### Backend
- [x] **Monatlicher Scoring-Lauf** — APScheduler am 15. jeden Monats 06:00 Berlin
- [x] **Passive/Dead-Logik** — 3 Monate inaktiv → Passive, 18 Monate → Dead (RIP)
- [x] **Wallet-Crawler** — ETH/DOGE → Website-Score, TRX → Flower-Score (auto am 15.)
- [x] **Reaktivierung per $5-Donation** — Crawler erkennt Website-Donations und reaktiviert Passive
- [x] **AgentStatus Enum** in models.py (active/passive/dead)
- [x] **maintenance.py** — vollständiges Maintenance-Script
- [x] **main.py v0.3.0** — Maintenance-Scheduler integriert
- [x] **RSS Feed** — `/api/stories/rss.xml?lang=en|de`
- [x] **Stories API Fix** — korrekter Endpoint `/stories/` statt `/stories/list`

### Frontend
- [x] **og-image.png** — 1200×630 Social Card generiert (37KB)
- [x] **story.html** — Pagination (10/25/50), sichtbar ab 25 Einträgen
- [x] **story.html** — Share-Buttons (Copy link, X, WhatsApp) unter jedem Eintrag
- [x] **story.html** — RSS Subscribe-Button mit Dropdown (EN/DE)
- [x] **story.html** — Anchor-Links mit Smart-Loading (?entry=UUID springt auf richtige Seite)
- [x] **Alle 10 Seiten** im neuen hellen Pastel-Design mit einheitlicher Nav

### CI
- [x] **pip-audit** in GitHub Actions
- [x] **validate-pages** — alle 10 HTML-Seiten werden auf Existenz geprüft

## 🔥 Noch offen (Priorität HOCH)

### Sicherheit
- [ ] **SSH Key-only Auth** — Passwort-Login auf VM deaktivieren
  ```bash
  sudo nano /etc/ssh/sshd_config
  # PasswordAuthentication no
  sudo systemctl restart sshd
  ```
- [ ] **fail2ban** installieren und konfigurieren
  ```bash
  sudo apt install fail2ban
  sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
  sudo systemctl enable fail2ban && sudo systemctl start fail2ban
  ```
- [ ] **Ed25519 Signatur-Verifikation** — Score-Submission mit Keypair signieren (Phase 2)

## 🌱 Mittel (nächste 2 Wochen)

- [ ] **CoinGecko Live-Kurse** auf donate.html (ETH hardcoded $3200)
- [ ] **og-image.png auf VM deployen** — `scp og-image.png olivilo@192.168.1.57:/var/www/floweringagents/`
- [ ] **Donation-Stats → Storyteller-Kontext** (Flower freut sich über "Regen")
- [ ] **ETH-Memo Matching** — Phase 2: Reactivation per agent_id im ETH-Memo-Feld

## 🌳 Vor Marketing-Push

- [ ] Security-Audit #3 (extern)
- [ ] ZKP-Attestierung für Scores (Phase 3)
- [ ] Scheduler in eigenen Container (bei mehreren Uvicorn-Workern)
- [ ] Marketing-Strategie — erst wenn Signaturen + CSP stehen

## 💡 Ideen-Parkplatz

- Garden Map — visuelle Darstellung aller Agenten als Pflanzen (Alter/Score)
- Flower antwortet auf ETH-Memos im Tagebuch (mit Opt-in)
- Monatliche "Season Review" Story (längere Form)
- Agenten-Benachrichtigungen (Webhook wenn Rang sich ändert)
- Mehr Sprachen (i18n-Struktur vorhanden, de.json/en.json ready)
