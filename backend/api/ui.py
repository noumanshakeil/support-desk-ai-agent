import json
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.schemas import TicketCreate
from backend.services import triage

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    tickets = await triage.list_tickets(db)
    return templates.TemplateResponse("index.html", {"request": request, "tickets": tickets, "title": "Support Desk AI Agent", "json": json})

@router.post("/ui/tickets")
async def ui_create(subject: str = Form(...), body: str = Form(...), requester: str = Form("customer@example.com"), db: AsyncSession = Depends(get_db)):
    await triage.create_and_triage(db, TicketCreate(subject=subject, body=body, requester=requester))
    return RedirectResponse("/", status_code=303)

@router.post("/ui/tickets/{ticket_id}/close")
async def ui_close(ticket_id: str, db: AsyncSession = Depends(get_db)):
    await triage.set_status(db, ticket_id, "closed")
    return RedirectResponse("/", status_code=303)
