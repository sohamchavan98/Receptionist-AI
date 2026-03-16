from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from call_store import get_all_calls, get_call_by_sid

router = APIRouter()


class CallRecord(BaseModel):
    call_sid: str
    caller: str
    transcript: str
    ai_reply: str
    created_at: datetime
    duration_seconds: Optional[int] = None


@router.get("/", response_model=List[CallRecord])
async def list_calls(limit: int = 50, offset: int = 0):
    return await get_all_calls(limit=limit, offset=offset)


@router.get("/{call_sid}", response_model=CallRecord)
async def get_call(call_sid: str):
    record = await get_call_by_sid(call_sid)
    if not record:
        raise HTTPException(status_code=404, detail="Call not found")
    return record


@router.get("/stats/summary")
async def stats():
    all_calls = await get_all_calls(limit=1000)
    return {
        "total_calls": len(all_calls),
        "today": sum(
            1 for c in all_calls
            if c["created_at"].date() == datetime.utcnow().date()
        ),
    }