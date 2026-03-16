from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather, Record
import logging

from config import settings
from pipeline import run_pipeline, run_pipeline_with_whisper
from call_store import save_call_record

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/voice", response_class=PlainTextResponse)
async def inbound_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
):
    logger.info(f"Inbound call: SID={CallSid} from={From}")

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action=f"{settings.BASE_URL}/twilio/gather",
        method="POST",
        timeout=5,
        speech_timeout="auto",
        language="en-US",
    )
    gather.say(
        "Hello, thank you for calling. How can I help you today?",
        voice="Polly.Joanna",
    )
    response.append(gather)
    response.say("Sorry, I didn't catch that. Please call back and try again.")

    return PlainTextResponse(str(response), media_type="application/xml")


@router.post("/gather", response_class=PlainTextResponse)
async def gather_response(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(default=""),
    SpeechResult: str = Form(default=""),
    Confidence: float = Form(default=0.0),
):
    logger.info(f"Gathered speech: '{SpeechResult}' (confidence={Confidence:.2f})")

    response = VoiceResponse()

    if not SpeechResult:
        response.say("I'm sorry, I didn't hear anything. Please try again.")
        response.redirect(f"{settings.BASE_URL}/twilio/voice", method="POST")
        return PlainTextResponse(str(response), media_type="application/xml")

    # Use Whisper if confidence is low, otherwise use Twilio's transcript
    if Confidence < 0.75:
        logger.info("Low confidence — routing to Whisper recording")
        response.say("One moment please.", voice="Polly.Joanna")
        response.record(
            action=f"{settings.BASE_URL}/twilio/recording",
            method="POST",
            max_length=30,
            play_beep=False,
            trim="trim-silence",
        )
        return PlainTextResponse(str(response), media_type="application/xml")

    # High confidence — use Twilio transcript directly (faster)
    try:
        ai_reply = await run_pipeline(
            transcript=SpeechResult,
            call_sid=CallSid,
            caller=From,
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        ai_reply = "I'm experiencing a technical issue. Please hold or call back shortly."

    gather = Gather(
        input="speech",
        action=f"{settings.BASE_URL}/twilio/gather",
        method="POST",
        timeout=5,
        speech_timeout="auto",
        language="en-US",
    )
    gather.say(ai_reply, voice="Polly.Joanna")
    response.append(gather)
    response.say("Thank you for calling. Goodbye!", voice="Polly.Joanna")
    response.hangup()

    await save_call_record(
        call_sid=CallSid,
        caller=From,
        transcript=SpeechResult,
        ai_reply=ai_reply,
    )

    return PlainTextResponse(str(response), media_type="application/xml")


@router.post("/recording", response_class=PlainTextResponse)
async def handle_recording(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(default=""),
    RecordingUrl: str = Form(default=""),
    RecordingDuration: str = Form(default="0"),
):
    """Handles recordings — runs Whisper STT for better accuracy."""
    logger.info(f"Recording received: {RecordingUrl}")

    response = VoiceResponse()

    try:
        ai_reply = await run_pipeline_with_whisper(
            recording_url=RecordingUrl,
            call_sid=CallSid,
            caller=From,
        )
    except Exception as e:
        logger.error(f"Whisper pipeline error: {e}")
        ai_reply = "I'm sorry, I had trouble understanding. Could you call back and try again?"

    gather = Gather(
        input="speech",
        action=f"{settings.BASE_URL}/twilio/gather",
        method="POST",
        timeout=5,
        speech_timeout="auto",
        language="en-US",
    )
    gather.say(ai_reply, voice="Polly.Joanna")
    response.append(gather)
    response.say("Thank you for calling. Goodbye!", voice="Polly.Joanna")
    response.hangup()

    await save_call_record(
        call_sid=CallSid,
        caller=From,
        transcript="[Whisper transcribed]",
        ai_reply=ai_reply,
    )

    return PlainTextResponse(str(response), media_type="application/xml")


@router.post("/status")
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    Duration: str = Form(default="0"),
):
    logger.info(f"Call {CallSid} ended: status={CallStatus}, duration={Duration}s")
    return {"ok": True}