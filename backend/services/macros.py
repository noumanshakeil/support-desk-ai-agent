DEFAULT_MACROS = {
    "reset_mfa": ("Reset MFA", "Walk the customer through MFA reset and confirm login."),
    "send_status": ("Send status", "Acknowledge the issue and share current investigation status."),
    "refund_policy": ("Refund policy", "Explain eligibility windows and next steps for refunds."),
    "escalate_tier2": ("Escalate T2", "Escalate with reproduction steps and impact summary."),
}

async def ensure_macros(session) -> None:
    from sqlalchemy import select
    from backend.models import Macro
    existing = {m.key for m in (await session.execute(select(Macro))).scalars()}
    for key, (title, body) in DEFAULT_MACROS.items():
        if key not in existing:
            session.add(Macro(key=key, title=title, body=body))
    await session.commit()
