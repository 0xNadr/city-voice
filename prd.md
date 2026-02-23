# CityVoice - Product Requirements Document

## 1. Overview

**Project Name:** CityVoice
**Description:** An LLM-powered VoiceBot prototype enabling citizens to interact via voice to inquire about city services and opening hours.
**Target Users:** Citizens seeking information about municipal services
**Scope:** Full-stack prototype (~4-6 hours development time)

---

## 2. Problem Statement

Citizens often struggle to find accurate, up-to-date information about city services and opening hours. Traditional methods (phone calls during business hours, website navigation) can be time-consuming and frustrating. A voice-based AI assistant provides 24/7 access to this information in a natural, conversational manner.

---

## 3. Solution

An Auto-Turn VoiceBot web application that:
- Accepts continuous voice input from users
- Processes speech through STT (Speech-to-Text)
- Uses LLM for intent recognition and response generation
- Calls appropriate tools based on user intent
- Returns responses via TTS (Text-to-Speech)

### User Flow
```
User opens web app → Clicks "Call" → Greeting plays →
User speaks question → Bot processes & responds via audio →
Continuous conversation until user hangs up
```

---

## 4. Core Features

### 4.1 Voice Interface (Frontend)
- **Call Button:** Initiates voice session with the bot
- **Hang Up Button:** Ends the current session
- **Opening Hours Display:** Visual display of department opening hours from `opening_hours.json`
- **Audio Visualization:** Optional visual feedback during speech

### 4.2 Voice Processing Pipeline (Backend)
| Stage | Technology | Description |
|-------|------------|-------------|
| STT | OpenAI Whisper | Convert user speech to text |
| LLM | OpenAI GPT-4 | Intent recognition & response generation |
| Tool Execution | Custom handlers | Execute getOpeningHours or queryKnowledgeBase |
| TTS | ElevenLabs | Convert response text to natural speech |

### 4.3 Tools

#### A) `getOpeningHours`
- **Purpose:** Retrieve opening hours for city departments
- **Data Source:** `opening_hours.json`
- **Input:** Department name (optional, returns all if not specified)
- **Output:** Opening hours for requested department(s)

#### B) `queryKnowledgeBase`
- **Purpose:** Answer questions about city services using RAG
- **Data Source:** ~600 Markdown files (city documentation)
- **Implementation:** Vector embeddings + similarity search
- **Output:** Contextually relevant answer based on retrieved documents

---

## 5. Technical Architecture

### 5.1 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js / TypeScript |
| Backend | Python (FastAPI) |
| Voice Pipeline | LiveKit or Pipecat |
| LLM | OpenAI GPT-4 |
| STT | OpenAI Whisper |
| TTS | ElevenLabs |
| Vector DB | ChromaDB / FAISS (for RAG) |
| Containerization | Docker / Docker Compose |

### 5.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Call Button │  │ Hang Up Btn │  │ Opening Hours Display   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                           │                                      │
│                    WebSocket / WebRTC                            │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                      BACKEND (Python)                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Voice Pipeline (LiveKit/Pipecat)           ││
│  │  ┌─────┐    ┌─────┐    ┌──────────┐    ┌─────┐             ││
│  │  │ STT │ -> │ LLM │ -> │ Tool Exec│ -> │ TTS │             ││
│  │  └─────┘    └─────┘    └──────────┘    └─────┘             ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              │                               │                   │
│  ┌───────────▼──────────┐      ┌────────────▼────────────┐     │
│  │  getOpeningHours     │      │  queryKnowledgeBase     │     │
│  │  (opening_hours.json)│      │  (RAG + Vector Store)   │     │
│  └──────────────────────┘      └─────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Project Structure

```
city-voice/
├── docker-compose.yml
├── README.md
├── PRD.md
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── public/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── voice_pipeline/
│   ├── tools/
│   │   ├── opening_hours.py
│   │   └── knowledge_base.py
│   ├── data/
│   │   ├── opening_hours.json
│   │   └── knowledge_base/
│   └── utils/
└── .env.example
```

---

## 6. API Specifications

### 6.1 WebSocket Endpoints

#### Voice Session
- **Endpoint:** `ws://localhost:8000/ws/voice`
- **Purpose:** Bidirectional audio streaming
- **Events:**
  - `session.start` - Initialize voice session
  - `audio.input` - Send audio chunks from client
  - `audio.output` - Receive audio response from server
  - `session.end` - Terminate session

### 6.2 REST Endpoints

#### Get Opening Hours
- **GET** `/api/opening-hours`
- **Response:** Full opening hours data

#### Health Check
- **GET** `/health`
- **Response:** `{ "status": "ok" }`

---

## 7. Data Models

### 7.1 Opening Hours Schema
```json
{
  "departments": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "hours": {
        "monday": { "open": "08:00", "close": "16:00" },
        "tuesday": { "open": "08:00", "close": "16:00" },
        ...
      },
      "exceptions": [
        { "date": "2024-12-25", "closed": true, "reason": "Weihnachten" }
      ]
    }
  ]
}
```

### 7.2 LLM Tool Definitions
```python
tools = [
    {
        "name": "getOpeningHours",
        "description": "Get opening hours for city departments",
        "parameters": {
            "department": {
                "type": "string",
                "description": "Name of the department (optional)"
            }
        }
    },
    {
        "name": "queryKnowledgeBase",
        "description": "Search the knowledge base for city service information",
        "parameters": {
            "query": {
                "type": "string",
                "description": "The user's question about city services"
            }
        }
    }
]
```

---

## 8. Non-Functional Requirements

### 8.1 Performance
- Voice response latency: < 2 seconds (target)
- Concurrent users: 1 (prototype scope)

### 8.2 Reliability
- Graceful error handling for API failures
- Fallback responses when tools fail

### 8.3 Usability
- Simple, intuitive UI
- Clear audio feedback
- German language support (primary)

---

## 9. Trade-offs & Decisions

| Decision | Rationale |
|----------|-----------|
| LiveKit vs Pipecat | Evaluate both; choose based on ease of integration |
| ChromaDB for RAG | Lightweight, easy to set up, sufficient for prototype |
| Single Docker Compose | Simplifies local development and deployment |
| OpenAI for STT/LLM | Best quality, provided API keys |
| ElevenLabs for TTS | Natural German voice output |

---

## 10. Out of Scope (Prototype)

- User authentication
- Session persistence
- Multi-language support (beyond German)
- Production deployment
- Comprehensive test coverage
- Advanced analytics
- Mobile-specific optimization

---

## 11. Success Criteria

- [ ] User can initiate and end voice calls via web interface
- [ ] Bot greets user upon call start
- [ ] Voice input is correctly transcribed
- [ ] LLM correctly identifies user intent
- [ ] `getOpeningHours` tool returns correct data
- [ ] `queryKnowledgeBase` tool returns relevant answers from markdown files
- [ ] TTS responses are clear and natural
- [ ] Application runs locally via Docker
- [ ] Opening hours are displayed in the frontend

---

## 12. Timeline Estimate

| Phase | Tasks |
|-------|-------|
| Setup | Docker, project structure, dependencies |
| Backend Core | Voice pipeline, STT/TTS integration |
| Tools | Implement getOpeningHours, queryKnowledgeBase (RAG) |
| Frontend | UI components, WebSocket connection |
| Integration | End-to-end testing, bug fixes |
| Documentation | README, code comments |

---

## 13. Resources

- **Opening Hours Data:** `backend/data/opening_hours.json`
- **Knowledge Base:** `backend/data/knowledge_base/` (Markdown files)
- **API Keys:** OpenAI & ElevenLabs (required)

---

*Document Version: 1.0*
*Last Updated: 2026-02-12*
