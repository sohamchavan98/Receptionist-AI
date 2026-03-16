from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    OLLAMA_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3"

    WHISPER_MODEL: str = "base"
    TTS_MODEL: str = "tts_models/en/ljspeech/tacotron2-DDC"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/receptionist"

    BASE_URL: str = ""
    SECRET_KEY: str = "change-me"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()