from __future__ import annotations
import json, uuid
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import Ticket
from backend.schemas import TicketCreate
from backend.services.macros import ensure_macros

log = structlog.get_logger(__name__)
SLA = {"urgent": 1, "high": 4, "medium": 24, "low": 72}

async def create_and_triage(session: AsyncSession, payload: TicketCreate) -> Ticket:
    await ensure_macros(session)
    ticket = Ticket(
        id=uuid.uuid4().hex[:10],
        subject=payload.subject.strip(),
        body=payload.body.strip(),
        requester=payload.requester,
        status="triaging",
    )
    session.add(ticket)
    await session.flush()
    llm = get_llm()
    result = await llm.complete_json(
        f"Triage this support ticket as JSON with priority, category, macros, reply, sla_hours.\n"
        f"Subject: {ticket.subject}\nBody: {ticket.body}",
        system="You are a senior support lead. Be concise and actionable.",
    )
    priority = str(result.get("priority") or "medium").lower()
    ticket.priority = priority if priority in SLA else "medium"
    ticket.category = str(result.get("category") or "general")
    macros = result.get("macros") or []
    ticket.macros_json = json.dumps(macros)
    ticket.reply_draft = str(result.get("reply") or "")
    ticket.sla_hours = int(result.get("sla_hours") or SLA[ticket.priority])
    ticket.status = "open"
    await session.commit()
    await session.refresh(ticket)
    log.info("ticket_triaged", ticket_id=ticket.id, priority=ticket.priority)
    return ticket

async def list_tickets(session: AsyncSession) -> list[Ticket]:
    rows = await session.execute(select(Ticket).order_by(Ticket.created_at.desc()).limit(100))
    return list(rows.scalars())

async def set_status(session: AsyncSession, ticket_id: str, status: str) -> Ticket:
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise ValueError("ticket not found")
    ticket.status = status
    await session.commit()
    await session.refresh(ticket)
    return ticket
