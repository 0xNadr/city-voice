# CityVoice - Sprachassistent für Ihre Stadt

Ein LLM-gestützter Sprachassistent, der Bürgern Informationen über städtische Dienstleistungen und Öffnungszeiten bereitstellt.

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (Next.js)                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              VoiceAgent Component                        ││
│  │         (@elevenlabs/client SDK)                         ││
│  │  ┌─────────┐  ┌──────────┐  ┌─────────────────────────┐ ││
│  │  │ Anrufen │  │ Auflegen │  │ Live Transcript         │ ││
│  │  └─────────┘  └──────────┘  └─────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                  │
│                      WebRTC                                  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│              ElevenLabs Conversational AI                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Agent: CityVoice                                        ││
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐ ││
│  │  │   ASR   │ → │  LLM    │ → │  Tools  │ → │   TTS   │ ││
│  │  │(Whisper)│   │(GPT-4o) │   │(Webhooks│   │(Turbo)  │ ││
│  │  └─────────┘   └─────────┘   └─────────┘   └─────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                  │
│                    Webhook Calls                             │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Tool Webhook Endpoints                    │  │
│  │  ┌─────────────────────┐  ┌─────────────────────────┐ │  │
│  │  │  /api/tools/        │  │  /api/tools/            │ │  │
│  │  │  opening-hours      │  │  knowledge-query        │ │  │
│  │  │  (JSON Data)        │  │  (ChromaDB RAG)         │ │  │
│  │  └─────────────────────┘  └─────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Komponente | Technologie |
|------------|-------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Voice SDK | @elevenlabs/client (WebRTC) |
| Backend | Python, FastAPI |
| Voice Agent | ElevenLabs Conversational AI |
| LLM | GPT-4o-mini (via ElevenLabs) |
| TTS | ElevenLabs Turbo v2.5 |
| Vector DB | ChromaDB |

## Features

- **Hands-free Sprachinteraktion**: WebRTC mit automatischer Spracherkennung (VAD)
- **Echtzeittranskription**: Live-Anzeige von Benutzer- und Agenten-Nachrichten
- **Öffnungszeiten**: Abruf von Öffnungszeiten städtischer Abteilungen
- **Wissensdatenbank**: RAG-basierte Suche in 566+ städtischen Dokumenten
- **Deutsche Sprache**: Vollständig auf Deutsch mit natürlicher Stimme

## Schnellstart

### Voraussetzungen

- Python 3.11+
- Node.js 18+
- ElevenLabs API Key (mit Conversational AI Zugang)

### 1. Repository klonen

```bash
git clone <repository-url>
cd city-voice
```

### 2. Backend einrichten

```bash
cd backend

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# .env konfigurieren
cp .env.example .env
# Bearbeiten Sie .env und fügen Sie Ihren ElevenLabs API Key hinzu
```

### 3. Frontend einrichten

```bash
cd frontend

# Dependencies installieren
npm install

# .env.local konfigurieren
cp .env.local.example .env.local
# Der Agent ID wird automatisch vom Setup-Script gesetzt
```

### 4. ElevenLabs Agent erstellen

```bash
# Vom Projekt-Root aus
cd city-voice

# Agent erstellen (setzt automatisch Agent ID in .env Dateien)
python scripts/setup_agent.py
```

### 5. Backend für Webhooks freigeben

Die ElevenLabs Agent-Tools benötigen öffentlichen Zugriff auf Ihr Backend:

```bash
# Option 1: localtunnel
npx localtunnel --port 8000

# Option 2: ngrok
ngrok http 8000
```

Dann Webhook-URLs aktualisieren:

```bash
python scripts/setup_agent.py --update-webhooks https://your-tunnel-url.com
```

### 6. Services starten

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev -- -p 3001
```

### 7. Testen

Öffnen Sie http://localhost:3001 und klicken Sie auf "Anrufen".

Beispielfragen:
- "Wann hat das Einwohnermeldeamt geöffnet?"
- "Wie beantrage ich einen Personalausweis?"
- "Was brauche ich für die Kfz-Zulassung?"

## Konfiguration

### Backend (.env)

```env
# ElevenLabs API Key
ELEVENLABS_API_KEY=sk_...

# ElevenLabs Agent ID (wird von setup_agent.py gesetzt)
ELEVENLABS_AGENT_ID=agent_...

# Webhook URL (wird von setup_agent.py --update-webhooks gesetzt)
WEBHOOK_BASE_URL=https://your-tunnel-url.com

# Data paths
OPENING_HOURS_PATH=./data/opening_hours.json
KNOWLEDGE_BASE_PATH=./data/knowledge_base
```

### Frontend (.env.local)

```env
# ElevenLabs Agent ID (wird von setup_agent.py gesetzt)
NEXT_PUBLIC_ELEVENLABS_AGENT_ID=agent_...

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpunkte

### REST Endpunkte

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/` | GET | API Info |
| `/health` | GET | Health Check |
| `/api/opening-hours` | GET | Alle Öffnungszeiten |
| `/api/knowledge/status` | GET | Knowledge Base Status |

### Tool Webhook Endpunkte

Diese Endpunkte werden vom ElevenLabs Agent aufgerufen:

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/tools/opening-hours` | POST | Öffnungszeiten abfragen |
| `/api/tools/knowledge-query` | POST | Wissensdatenbank durchsuchen |

**Request Format (opening-hours):**
```json
{"department": "Einwohnermeldeamt"}
```

**Request Format (knowledge-query):**
```json
{"query": "Wie beantrage ich einen Personalausweis?"}
```

## Projektstruktur

```
city-voice/
├── README.md
├── prd.md
│
├── scripts/
│   └── setup_agent.py       # Agent erstellen/aktualisieren
│
├── backend/
│   ├── .env                 # Backend Konfiguration
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py          # FastAPI App + Webhook Endpoints
│   │   ├── config.py        # Settings
│   │   ├── services/
│   │   │   └── knowledge_base.py   # ChromaDB Service
│   │   └── tools/
│   │       ├── opening_hours.py    # Öffnungszeiten Tool
│   │       └── knowledge_query.py  # Knowledge Query Tool
│   └── data/
│       ├── opening_hours.json      # Öffnungszeiten Daten
│       └── knowledge_base/         # Markdown Dokumente (566 Dateien)
│
└── frontend/
    ├── .env.local           # Frontend Konfiguration
    ├── package.json
    └── src/
        ├── app/
        │   └── page.tsx     # Hauptseite
        └── components/
            ├── VoiceAgent.tsx      # ElevenLabs Voice Agent
            └── OpeningHours.tsx    # Öffnungszeiten Anzeige
```

## Setup Script Befehle

```bash
# Neuen Agent erstellen
python scripts/setup_agent.py

# Webhook URLs aktualisieren
python scripts/setup_agent.py --update-webhooks https://your-url.com

# Verfügbare Stimmen anzeigen
python scripts/setup_agent.py --list-voices

# Agent-Info anzeigen
python scripts/setup_agent.py --info
```

## Agent Konfiguration

Der ElevenLabs Agent ist konfiguriert mit:

| Einstellung | Wert |
|-------------|------|
| Name | CityVoice |
| Sprache | Deutsch (de) |
| Stimme | Sarah (Mature, Reassuring) |
| TTS Modell | eleven_turbo_v2_5 |
| LLM | gpt-4o-mini |
| Tools | getOpeningHours, queryKnowledgeBase |

## Daten

### Öffnungszeiten (opening_hours.json)

```json
{
  "Einwohnermeldeamt": {
    "Montag": "08:00-12:00,13:00-16:00",
    "Dienstag": "08:00-12:00",
    ...
  },
  "Standesamt": { ... },
  "Kfz-Zulassungsstelle": { ... },
  "Sozialamt": { ... }
}
```

### Wissensdatenbank

566 Markdown-Dokumente mit Informationen zu städtischen Dienstleistungen:
- Personalausweis beantragen
- Reisepass beantragen
- Hundesteuer anmelden
- Kfz-Zulassung
- und mehr...

## Troubleshooting

### Agent antwortet nicht auf Tool-Anfragen

1. Prüfen Sie ob der Tunnel aktiv ist:
   ```bash
   curl https://your-tunnel-url.com/health
   ```

2. Webhook URLs aktualisieren:
   ```bash
   python scripts/setup_agent.py --update-webhooks https://new-tunnel-url.com
   ```

### Stimme klingt falsch

Stimme ändern:
```python
# In scripts/setup_agent.py die SELECTED_VOICE anpassen
# Verfügbare Stimmen: Nicole, Matilda, Charlie, Sarah, Alice, etc.
```

### Knowledge Base ist leer

```bash
# Backend neu starten - seeded automatisch beim Start
cd backend && uvicorn app.main:app --reload
```

## Lizenz

Prototyp für städtische Dienstleistungen
