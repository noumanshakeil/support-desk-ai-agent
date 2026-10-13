import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.schemas import TicketCreate, TicketOut
from backend.services import triage

router = APIRouter()

def to_out(t) -> TicketOut:
    return TicketOut(
        id=t.id, subject=t.subject, body=t.body, requester=t.requester, status=t.status,
        priority=t.priority, category=t.category, macros=json.loads(t.macros_json or "[]"),
        reply_draft=t.reply_draft, sla_hours=t.sla_hours, created_at=t.created_at,
    )

@router.get("", response_model=list[TicketOut])
async def list_tickets(db: AsyncSession = Depends(get_db)) -> list[TicketOut]:
    return [to_out(t) for t in await triage.list_tickets(db)]

@router.post("", response_model=TicketOut)
async def create_ticket(payload: TicketCreate, db: AsyncSession = Depends(get_db)) -> TicketOut:
    return to_out(await triage.create_and_triage(db, payload))

@router.post("/{ticket_id}/status/{status}", response_model=TicketOut)
async def update_status(ticket_id: str, status: str, db: AsyncSession = Depends(get_db)) -> TicketOut:
    try:
        return to_out(await triage.set_status(db, ticket_id, status))
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
