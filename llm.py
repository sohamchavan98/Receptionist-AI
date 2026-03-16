import httpx
import logging
from config import settings
from receptionist import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

OLLAMA_CHAT_URL = f"{settings.OLLAMA_URL}/api/chat"


async def ask_llm(user_message: str, conversation_history: list = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "num_predict": 150,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(OLLAMA_CHAT_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
            reply = data["message"]["content"].strip()
            logger.info(f"LLM reply: {reply[:80]}...")
            return reply

    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama. Is `ollama serve` running?")
        raise RuntimeError("LLM unavailable — Ollama not running")
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise