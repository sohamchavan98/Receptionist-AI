import pyttsx3
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


def generate_speech(text: str) -> str:
    """
    Convert text to speech and save as a WAV file.
    
    Args:
        text: The text to speak
        
    Returns:
        Path to the generated WAV file
    """
    logger.info(f"Generating speech for: '{text[:50]}...'")

    # Create a temp file to save audio
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    engine = pyttsx3.init()

    # Voice settings
    engine.setProperty("rate", 165)      # Speed — 165 words per minute feels natural
    engine.setProperty("volume", 1.0)    # Full volume

    # Use a female voice if available
    voices = engine.getProperty("voices")
    for voice in voices:
        if "female" in voice.name.lower() or "zira" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

    engine.save_to_file(text, temp_path)
    engine.runAndWait()

    logger.info(f"Speech saved to: {temp_path}")
    return temp_path


def list_voices():
    """Helper to see all available voices on your system."""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for i, voice in enumerate(voices):
        print(f"{i}: {voice.name} | {voice.id}")