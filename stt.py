import whisper
import tempfile
import os
import logging
import httpx

logger = logging.getLogger(__name__)

# Load model once at startup — "small" is best balance of speed vs accuracy
_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading Whisper model (first time only)...")
        _model = whisper.load_model("tiny")
        logger.info("Whisper model loaded.")
    return _model


async def transcribe_from_url(audio_url: str, twilio_sid: str, twilio_token: str) -> str:
    """
    Download audio from Twilio recording URL and transcribe with Whisper.
    
    Args:
        audio_url: Twilio recording URL
        twilio_sid: Your Twilio Account SID (for auth)
        twilio_token: Your Twilio Auth Token (for auth)
    
    Returns:
        Transcribed text string
    """
    logger.info(f"Downloading audio from: {audio_url}")

    # Download the audio file from Twilio
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            audio_url + ".wav",
            auth=(twilio_sid, twilio_token),
            timeout=30.0
        )
        resp.raise_for_status()

    # Save to a temp file and transcribe
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(resp.content)
        temp_path = f.name

    try:
        model = get_model()
        logger.info("Transcribing audio with Whisper...")
        result = model.transcribe(temp_path, language="en", fp16=False)
        transcript = result["text"].strip()
        logger.info(f"Whisper transcript: '{transcript}'")
        return transcript
    finally:
        os.unlink(temp_path)  # Clean up temp file


def transcribe_from_file(file_path: str) -> str:
    """Transcribe a local audio file — useful for testing."""
    model = get_model()
    result = model.transcribe(file_path, language="en", fp16=False)
    return result["text"].strip()