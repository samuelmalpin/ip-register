from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


async def add_audit_log(
    db: AsyncSession,
    user_id: int | None,
    action: str,
    entity: str,
    entity_id: int | None,
) -> None:
    db.add(AuditLog(user_id=user_id, action=action, entity=entity, entity_id=entity_id))
    await db.commit()
