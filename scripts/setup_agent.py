#!/usr/bin/env python3
"""
Setup script for creating/updating the CityVoice ElevenLabs Conversational Agent.

Usage:
    python scripts/setup_agent.py                    # Create new agent
    python scripts/setup_agent.py --update-webhooks  # Update webhook URLs
    python scripts/setup_agent.py --list-voices      # List available voices

Requirements:
    - ELEVENLABS_API_KEY in backend/.env
"""

import os
import sys
import json
import requests
from pathlib import Path

# Load environment from backend/.env
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_ENV = PROJECT_ROOT / "backend" / ".env"

def load_env():
    """Load environment variables from backend/.env"""
    env_vars = {}
    if BACKEND_ENV.exists():
        with open(BACKEND_ENV) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
                    os.environ[key.strip()] = value.strip()
    return env_vars

env = load_env()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")

if not ELEVENLABS_API_KEY:
    print(f"Error: ELEVENLABS_API_KEY not found in {BACKEND_ENV}")
    sys.exit(1)

# German voice IDs from ElevenLabs
GERMAN_VOICES = {
    "Nicole": "piTKgcLEGmPE4e6mEKli",
    "Matilda": "XrExE9yKIg1WjnnlVkGX",
    "Charlie": "IKne3meq5aSn9XLyUdCD",
}
SELECTED_VOICE = GERMAN_VOICES["Nicole"]

# System prompt for CityVoice
SYSTEM_PROMPT = """Du bist CityVoice, der virtuelle Sprachassistent der Hansestadt Lüneburg.

Deine Aufgaben:
- Du hilfst Bürgern bei Fragen zu städtischen Dienstleistungen und Öffnungszeiten
- Du bist freundlich, hilfsbereit und professionell
- Du antwortest immer auf Deutsch
- Du hältst deine Antworten kurz und präzise (2-3 Sätze)

Wichtige Hinweise:
- Nutze das Tool "getOpeningHours" wenn jemand nach Öffnungszeiten fragt
- Nutze das Tool "queryKnowledgeBase" für allgemeine Fragen zu städtischen Dienstleistungen
- Wenn du keine Information hast, sage ehrlich dass du es nicht weißt und empfehle den Kontakt zur Stadt

Beispiele für Fragen die du beantworten kannst:
- Wann hat das Einwohnermeldeamt geöffnet?
- Wie kann ich einen Personalausweis beantragen?
- Was brauche ich für die Kfz-Zulassung?
"""

FIRST_MESSAGE = "Guten Tag! Willkommen bei CityVoice, dem Sprachassistenten der Stadt Lüneburg. Wie kann ich Ihnen heute helfen?"


def get_tools(webhook_url: str) -> list:
    """Get tool definitions with the specified webhook URL."""
    return [
        {
            "type": "webhook",
            "name": "getOpeningHours",
            "description": "Gibt die Öffnungszeiten für städtische Abteilungen zurück. Nutze dieses Tool wenn jemand nach Öffnungszeiten fragt.",
            "api_schema": {
                "url": f"{webhook_url}/api/tools/opening-hours",
                "method": "POST",
                "request_body_schema": {
                    "type": "object",
                    "properties": {
                        "department": {
                            "type": "string",
                            "description": "Name der Abteilung (z.B. Einwohnermeldeamt, Standesamt, Kfz-Zulassungsstelle). Optional."
                        }
                    }
                },
                "request_headers": {"Content-Type": "application/json"}
            },
            "response_timeout_secs": 10
        },
        {
            "type": "webhook",
            "name": "queryKnowledgeBase",
            "description": "Durchsucht die Wissensdatenbank nach Informationen zu städtischen Dienstleistungen.",
            "api_schema": {
                "url": f"{webhook_url}/api/tools/knowledge-query",
                "method": "POST",
                "request_body_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Die Frage des Benutzers"
                        }
                    },
                    "required": ["query"]
                },
                "request_headers": {"Content-Type": "application/json"}
            },
            "response_timeout_secs": 15
        }
    ]


def create_agent(webhook_url: str = None) -> str:
    """Create a new CityVoice agent."""
    url = "https://api.elevenlabs.io/v1/convai/agents/create"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    webhook_url = webhook_url or WEBHOOK_BASE_URL
    tools = get_tools(webhook_url)

    payload = {
        "name": "CityVoice Lüneburg",
        "tags": ["cityvoice", "luneburg", "german"],
        "conversation_config": {
            "agent": {
                "first_message": FIRST_MESSAGE,
                "language": "de",
                "prompt": {
                    "prompt": SYSTEM_PROMPT,
                    "llm": "gpt-4o-mini",
                    "temperature": 0.7,
                    "tools": tools
                }
            },
            "tts": {
                "voice_id": SELECTED_VOICE,
                "model_id": "eleven_turbo_v2_5",
                "optimize_streaming_latency": 2,
                "stability": 0.5,
                "similarity_boost": 0.75
            },
            "asr": {
                "quality": "high",
                "provider": "elevenlabs"
            },
            "turn": {
                "turn_timeout": 10,
                "silence_end_call_timeout": 30
            },
            "conversation": {
                "max_duration_seconds": 600
            }
        },
        "platform_settings": {
            "widget": {
                "variant": "compact",
                "feedback_mode": "none",
                "text_input_enabled": True
            }
        }
    }

    print("Creating CityVoice agent...")
    print(f"Webhook URL: {webhook_url}")
    print()

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        agent_id = data.get("agent_id")

        print("=" * 60)
        print("SUCCESS! Agent created.")
        print("=" * 60)
        print(f"\nAgent ID: {agent_id}")
        print(f"\nUpdate backend/.env with:")
        print(f"  ELEVENLABS_AGENT_ID={agent_id}")
        print(f"\nUpdate frontend/.env.local with:")
        print(f"  NEXT_PUBLIC_ELEVENLABS_AGENT_ID={agent_id}")

        # Update backend/.env with agent ID
        update_env_file(BACKEND_ENV, "ELEVENLABS_AGENT_ID", agent_id)

        # Update frontend/.env.local
        frontend_env = PROJECT_ROOT / "frontend" / ".env.local"
        update_env_file(frontend_env, "NEXT_PUBLIC_ELEVENLABS_AGENT_ID", agent_id)

        return agent_id
    else:
        print(f"Error creating agent: {response.status_code}")
        print(response.text)
        return None


def update_agent_webhooks(agent_id: str, webhook_url: str) -> bool:
    """Update an existing agent's webhook URLs."""
    url = f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    tools = get_tools(webhook_url)

    # We need to update the agent's conversation_config.agent.prompt.tools
    payload = {
        "conversation_config": {
            "agent": {
                "prompt": {
                    "tools": tools
                }
            }
        }
    }

    print(f"Updating agent {agent_id} webhook URLs...")
    print(f"New webhook URL: {webhook_url}")
    print()

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("=" * 60)
        print("SUCCESS! Webhook URLs updated.")
        print("=" * 60)
        print(f"\nTools now point to:")
        print(f"  - {webhook_url}/api/tools/opening-hours")
        print(f"  - {webhook_url}/api/tools/knowledge-query")

        # Update WEBHOOK_BASE_URL in backend/.env
        update_env_file(BACKEND_ENV, "WEBHOOK_BASE_URL", webhook_url)

        return True
    else:
        print(f"Error updating agent: {response.status_code}")
        print(response.text)
        return False


def update_env_file(env_path: Path, key: str, value: str):
    """Update or add a key in an env file."""
    lines = []
    found = False

    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith(f"{key}=") or line.strip().startswith(f"# {key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f"\n{key}={value}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)

    print(f"Updated {env_path}: {key}={value}")


def list_voices():
    """List available voices."""
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        voices = response.json().get("voices", [])
        print("\nAvailable voices:")
        print("-" * 50)
        for voice in voices[:20]:
            labels = voice.get("labels", {})
            print(f"  {voice['name']}: {voice['voice_id']}")
    else:
        print(f"Error: {response.status_code}")


def get_agent_info(agent_id: str):
    """Get agent information."""
    url = f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list-voices":
            list_voices()
        elif sys.argv[1] == "--update-webhooks":
            if len(sys.argv) < 3:
                print("Usage: python setup_agent.py --update-webhooks <webhook_url>")
                print("Example: python setup_agent.py --update-webhooks https://abc123.ngrok.io")
                sys.exit(1)

            webhook_url = sys.argv[2].rstrip("/")
            agent_id = ELEVENLABS_AGENT_ID

            if not agent_id:
                print("Error: ELEVENLABS_AGENT_ID not found in backend/.env")
                print("Run without --update-webhooks first to create an agent")
                sys.exit(1)

            update_agent_webhooks(agent_id, webhook_url)
        elif sys.argv[1] == "--info":
            agent_id = ELEVENLABS_AGENT_ID or (sys.argv[2] if len(sys.argv) > 2 else None)
            if agent_id:
                info = get_agent_info(agent_id)
                if info:
                    print(json.dumps(info, indent=2))
            else:
                print("No agent ID specified")
        else:
            print("Unknown option. Use --list-voices, --update-webhooks <url>, or --info")
    else:
        # Create new agent
        create_agent()
