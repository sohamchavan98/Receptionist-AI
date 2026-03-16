from datetime import datetime
from typing import Optional
import logging
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, CallRecord

logger = logging.getLogger(__name__)


async def save_call_record(
    call_sid: str,
    caller: str,
    transcript: str,
    ai_reply: str,
    duration_seconds: Optional[int] = None,
):
    async with AsyncSessionLocal() as session:
        try:
            # Check if record already exists
            result = await session.execute(
                select(CallRecord).where(CallRecord.call_sid == call_sid)
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                existing.transcript = transcript
                existing.ai_reply = ai_reply
                existing.duration_seconds = duration_seconds
            else:
                # Create new record
                record = CallRecord(
                    call_sid=call_sid,
                    caller=caller,
                    transcript=transcript,
                    ai_reply=ai_reply,
                    duration_seconds=duration_seconds,
                )
                session.add(record)

            await session.commit()
            logger.info(f"Saved call record: {call_sid}")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving call record: {e}")
            raise


async def get_all_calls(limit: int = 50, offset: int = 0) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CallRecord)
            .order_by(desc(CallRecord.created_at))
            .limit(limit)
            .offset(offset)
        )
        records = result.scalars().all()
        return [
            {
                "call_sid": r.call_sid,
                "caller": r.caller,
                "transcript": r.transcript,
                "ai_reply": r.ai_reply,
                "created_at": r.created_at,
                "duration_seconds": r.duration_seconds,
            }
            for r in records
        ]


async def get_call_by_sid(call_sid: str) -> Optional[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CallRecord).where(CallRecord.call_sid == call_sid)
        )
        r = result.scalar_one_or_none()
        if not r:
            return None
        return {
            "call_sid": r.call_sid,
            "caller": r.caller,
            "transcript": r.transcript,
            "ai_reply": r.ai_reply,
            "created_at": r.created_at,
            "duration_seconds": r.duration_seconds,
        }