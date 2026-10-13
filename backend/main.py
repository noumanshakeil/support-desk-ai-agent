"""Support Desk AI Agent — FastAPI backend + Jinja UI."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .llm import complete

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data" / "store.json"
FIELDS = ['subject', 'body', 'priority']

app = FastAPI(title="Support Desk AI Agent", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def load_store() -> dict:
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        payload = {"tickets": [
  {
    "id": "t1",
    "subject": "Cannot login",
    "priority": "high",
    "status": "open"
  },
  {
    "id": "t2",
    "subject": "Invoice typo",
    "priority": "low",
    "status": "open"
  }
]}
        DATA.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return json.loads(DATA.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(store, indent=2), encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "support-desk-ai-agent", "llm_mode": settings.llm_mode}


@app.get("/api/tickets")
def list_items() -> dict:
    store = load_store()
    return {"tickets": store.get("tickets", [])}


@app.post("/api/tickets")
def create_item(payload: dict) -> dict:
    store = load_store()
    item = {"id": uuid.uuid4().hex[:8]}
    for key in FIELDS:
        item[key] = payload.get(key)
    store.setdefault("tickets", []).insert(0, item)
    save_store(store)
    return item


@app.post("/api/triage")
def run_action(payload: dict) -> dict:
    """Suggest priority, macros, and next reply."""
    prompt = (
        "You are the AI engine for Support Desk AI Agent.\n"
        "Task: Suggest priority, macros, and next reply.\n"
        f"Input JSON: {json.dumps(payload)[:4000]}"
    )
    text = complete(prompt)
    return {"ok": True, "action": "triage", "result": text, "mode": settings.llm_mode}


@app.get("/", response_class=HTMLResponse)
def home(request: Request, last_result: str | None = None) -> HTMLResponse:
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Support Desk AI Agent",
            "description": "Ticket triage agent with SLA hints, macro suggestions, and a support inbox UI backed by FastAPI.",
            "resource": "tickets",
            "action": "triage",
            "action_desc": "Suggest priority, macros, and next reply",
            "items": store.get("tickets", []),
            "llm_mode": settings.llm_mode,
            "last_result": last_result,
        },
    )


@app.post("/ui/create", response_class=HTMLResponse)
async def ui_create(request: Request) -> HTMLResponse:
    form = await request.form()
    data = {k: form.get(k) for k in FIELDS}
    create_item(data)
    return home(request)


@app.post("/ui/action", response_class=HTMLResponse)
async def ui_action(request: Request, prompt: str = Form("demo")) -> HTMLResponse:
    result = run_action({"prompt": prompt})
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Support Desk AI Agent",
            "description": "Ticket triage agent with SLA hints, macro suggestions, and a support inbox UI backed by FastAPI.",
            "resource": "tickets",
            "action": "triage",
            "action_desc": "Suggest priority, macros, and next reply",
            "items": store.get("tickets", []),
            "llm_mode": settings.llm_mode,
            "last_result": result.get("result"),
        },
    )
