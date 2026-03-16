# Receptionist AI — Phase 1

AI-powered phone receptionist using **Twilio** (calls) + **Ollama/Llama 3** (local LLM, free) + **FastAPI** (backend).

## Architecture

```
Caller → Twilio → FastAPI /twilio/voice
                       ↓
               FastAPI /twilio/gather
                       ↓
               Ollama (local LLM)    ← runs on YOUR machine, zero API cost
                       ↓
               TwiML reply → Twilio → Caller hears AI response
```

---

## Prerequisites

| Tool | Install |
|------|---------|
| Python 3.12+ | https://python.org |
| Ollama | https://ollama.com — then `ollama pull llama3` |
| ngrok | https://ngrok.com (free account) — exposes localhost to Twilio |
| Twilio account | https://twilio.com (free trial = ~$15 credit) |
| Docker (optional) | For Postgres in Phase 3 |

---

## Local setup (5 steps)

### 1. Clone and install

```bash
git clone <your-repo>
cd receptionist-ai/backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — fill in Twilio credentials and set BASE_URL after step 4
```

### 3. Start Ollama

```bash
# In a separate terminal:
ollama serve

# First time — pull the model (~4GB download):
ollama pull llama3
```

### 4. Start ngrok

```bash
# In a separate terminal:
ngrok http 8000

# Copy the https URL (e.g. https://abc123.ngrok.io)
# Paste it as BASE_URL in your .env file
```

### 5. Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs — you'll see the interactive API docs.

---

## Configure Twilio webhook

1. Log in to https://console.twilio.com
2. Go to **Phone Numbers → Manage → Active numbers**
3. Click your number
4. Under **Voice Configuration → A call comes in**:
   - Set to **Webhook**
   - URL: `https://your-ngrok-url.ngrok.io/twilio/voice`
   - Method: `HTTP POST`
5. Save

Now call your Twilio number. The AI will answer!

---

## Customise the AI persona

Edit `app/prompts/receptionist.py`:

```python
SYSTEM_PROMPT = """You are a professional AI receptionist for [YOUR BUSINESS]...
"""
```

This file is version-controlled — commit changes here to track prompt history.

---

## Test without calling

```bash
# Simulate a Twilio webhook
curl -X POST http://localhost:8000/twilio/gather \
  -d "CallSid=test123" \
  -d "From=%2B15551234567" \
  -d "SpeechResult=What are your opening hours?" \
  -d "Confidence=0.95"
```

You should see the LLM reply in the response XML.

---

## Project structure

```
backend/
├── app/
│   ├── main.py              ← FastAPI app
│   ├── config.py            ← All settings (env vars)
│   ├── routes/
│   │   ├── twilio.py        ← Webhook handlers (/twilio/voice, /gather)
│   │   └── calls.py         ← REST API for dashboard (/calls/)
│   ├── services/
│   │   ├── llm.py           ← Ollama client
│   │   ├── pipeline.py      ← Orchestrator (STT → LLM → TTS)
│   │   └── call_store.py    ← In-memory store (Phase 1) / Postgres (Phase 3)
│   └── prompts/
│       └── receptionist.py  ← System prompt — edit this for your business
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## What's next (Phase 2)

- Replace Twilio's built-in STT with local **Whisper** for better accuracy
- Add **Coqui TTS** to generate custom voice audio (instead of Twilio's Polly)
- Stream LLM output to TTS as it generates (reduces latency to <1s)

## What's next (Phase 3)

- Swap in-memory call store for **Postgres + pgvector**
- Store embeddings of transcripts for semantic search
- Build React admin dashboard

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Cannot connect to Ollama` | Run `ollama serve` in a separate terminal |
| Twilio says "Application Error" | Check ngrok is running and BASE_URL is set correctly |
| No speech detected | Speak clearly; increase `timeout` in `twilio.py` |
| LLM replies are too long | Lower `num_predict` in `llm.py` options |
