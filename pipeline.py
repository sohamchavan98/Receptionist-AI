import logging
from llm import ask_llm
from stt import transcribe_from_url
from config import settings

logger = logging.getLogger(__name__)

_conversations: dict[str, list] = {}


async def run_pipeline(
    transcript: str,
    call_sid: str,
    caller: str,
) -> str:
    """Phase 1 pipeline — uses Twilio's built-in STT transcript."""
    logger.info(f"Pipeline: call={call_sid} transcript='{transcript[:60]}'")

    history = _conversations.get(call_sid, [])
    reply = await ask_llm(user_message=transcript, conversation_history=history)

    history.append({"role": "user", "content": transcript})
    history.append({"role": "assistant", "content": reply})
    _conversations[call_sid] = history[-12:]

    return reply


async def run_pipeline_with_whisper(
    recording_url: str,
    call_sid: str,
    caller: str,
) -> str:
    """Phase 2 pipeline — downloads Twilio recording and uses Whisper STT."""
    logger.info(f"Whisper pipeline: call={call_sid}")

    # Step 1: Transcribe with Whisper
    transcript = await transcribe_from_url(
        audio_url=recording_url,
        twilio_sid=settings.TWILIO_ACCOUNT_SID,
        twilio_token=settings.TWILIO_AUTH_TOKEN,
    )

    if not transcript:
        return "I'm sorry, I couldn't hear you clearly. Could you repeat that?"

    # Step 2: Get LLM reply
    history = _conversations.get(call_sid, [])
    reply = await ask_llm(user_message=transcript, conversation_history=history)

    history.append({"role": "user", "content": transcript})
    history.append({"role": "assistant", "content": reply})
    _conversations[call_sid] = history[-12:]

    logger.info(f"Whisper transcript: '{transcript}' → Reply: '{reply[:60]}'")
    return reply


def clear_conversation(call_sid: str):
    _conversations.pop(call_sid, None)