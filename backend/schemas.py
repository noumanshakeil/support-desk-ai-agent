from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=240)
    body: str = Field(min_length=3)
    requester: str = "customer@example.com"

class TicketOut(BaseModel):
    id: str
    subject: str
    body: str
    requester: str
    status: str
    priority: str
    category: str
    macros: list[str]
    reply_draft: str
    sla_hours: int
    created_at: datetime

class HealthOut(BaseModel):
    status: str
    service: str
    version: str
    llm_mode: str
