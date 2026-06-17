# MCP-Registry-Eintrag — Anleitung für Oliver
**Status: Vorbereitet, wartet auf Ausführung durch Oliver (erfordert interaktiven GitHub-Login)**

## Warum das wichtig ist
`registry.modelcontextprotocol.io` ist das offizielle Verzeichnis, in dem Claude Desktop, Claude Code und andere MCP-Clients aktiv nach verfügbaren Servern suchen. Der MCP-Server ist bereits auf PyPI veröffentlicht (`floweringagents-mcp`) und funktioniert eigenständig — der Registry-Eintrag macht ihn zusätzlich **auffindbar**, ohne dass jemand vorher den genauen Paketnamen kennen muss.

## Voraussetzungen (bereits erledigt)
- [x] `floweringagents-mcp` ist auf PyPI live
- [x] `mcp-server/server.json` liegt bereits im Repo vor, nach offiziellem Schema

## Schritte (nur du kannst das ausführen — GitHub-OAuth-Login)

**1. CLI-Tool installieren**
```bash
npm install -g mcp-publisher
```

**2. Bei GitHub einloggen (öffnet Browser-Fenster)**
```bash
cd /Volumes/M4Data/Coding/FloweringAgents/mcp-server
mcp-publisher login github
```
Das öffnet eine GitHub-OAuth-Seite in deinem Browser — du bestätigst dort mit deinem eigenen GitHub-Account. Das ist der Grund, warum ich (Claude) das nicht für dich ausführen kann.

**3. Veröffentlichen**
```bash
mcp-publisher publish
```
Das CLI-Tool liest automatisch die vorhandene `server.json` in diesem Ordner und sendet sie an die Registry.

**4. Verifizieren**
Nach ein paar Minuten sollte der Server unter folgender URL auftauchen:
```
https://registry.modelcontextprotocol.io/v0/servers?search=floweringagents
```
Oder direkt in Claude Desktop/Code unter den durchsuchbaren MCP-Servern.

## Falls ein Fehler auftritt
- **"Package not found on PyPI"** → kurz warten, PyPI-Indexierung kann ein paar Minuten dauern
- **"server.json validation failed"** → mir (Claude) die Fehlermeldung schicken, ich passe `mcp-server/server.json` entsprechend an
- **Login schlägt fehl** → sicherstellen, dass du mit dem GitHub-Account eingeloggt bist, der auch `github.com/olivilo/FloweringAgents` besitzt (Repo-Ownership wird oft zur Verifikation genutzt)

## Nach erfolgreicher Veröffentlichung
Sag mir Bescheid, dann markiere ich diesen Punkt in `roadmap.md` als erledigt und kann den Eintrag in `marketing/README.md` als ✅ abhaken.
