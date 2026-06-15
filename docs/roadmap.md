# 🗺️ FloweringAgents — Roadmap & TODOs
**Stand: 15. Juni 2026 (Tag 5)**

## ✅ Erledigt in Tag 5

### Regression-Fix (Tag 4 hatte Diary-Crash riskiert)
- [x] **models.py** — `agent_id` (PK), `months_active`, `first_commit_date` wiederhergestellt; `status`/`genesis_mult` additiv behalten; tote `ScoreEntry`-Tabelle entfernt
- [x] **database.py** — additive Migration (`ALTER TABLE agents ADD COLUMN IF NOT EXISTS status/genesis_mult`) für das bestehende v0.2.0-Prod-Schema
- [x] **routers/agents.py** — `is_active` → `status != dead`
- [x] **maintenance.py** — `Agent.id` → `agent_id`, `ScoreEntry` → `DailyScore` für Last-Activity-Check; Status-Logs (DEAD/PASSIVE/REACTIVATED) nur noch bei echtem Wechsel
- [x] **CI** — kaputtes YAML im pip-audit-Step von `ci.yml` gefixt

### Sicherheit
- [x] **Ed25519 Signatur-Verifikation** — `POST /scores/submit` mit optionaler Signatur, Verified-Upgrade (transparency_level 1→2); `GET /scores/keygen` mit Setup-Anleitung

Alle Punkte per Smoke-Tests (SQLite) + `ruff check` verifiziert, nach `origin/main` und `v2/main` gepusht (Commit `7264447`).

### Deploy auf der VM (15.06., abends)
- [x] `git pull` (66107d0 → 60071b6), Backend neu gebaut & gestartet — `/api/health` meldet jetzt **v0.3.0**
- [x] Additive Migration lief automatisch (`status`, `genesis_mult` in `agents` ergänzt)
- [x] Frontend-Statics nach `/var/www/floweringagents/` kopiert
- [x] **og-image.png** war im Repo nur ein 11-Byte-Platzhalter (seit Tag 4) — echte 1200×630 Social Card generiert, committed & deployed
- [x] **CSP-Header live geschaltet** — Bug im `infra/nginx.conf` gefixt (mehrzeilige Strings wurden von nginx nicht verkettet → `add_header` Syntaxfehler), `nginx -t` + reload, alle 10 Seiten + API verifiziert (200 OK)

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
- [ ] **GitHub-PAT aus VM-Git-Remote entfernen** — `origin` nutzt aktuell einen Personal Access Token in der Remote-URL (`.git/config` auf der VM). Auf Deploy-Key oder SSH-Remote umstellen, Token danach auf GitHub rotieren.

## 🌱 Mittel (nächste 2 Wochen)

- [ ] **CoinGecko Live-Kurse** auf donate.html (ETH hardcoded $3200)
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
