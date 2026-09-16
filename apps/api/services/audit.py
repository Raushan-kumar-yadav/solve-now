from sqlalchemy.orm import Session
from models.security import AuditLog

def log_audit_event(
    db: Session,
    action: str,
    details: str,
    user_id: str = None,
    ip_address: str = None,
    resource_type: str = "AUTH",
    resource_id: str = None
):
    audit = AuditLog(
        action=action,
        details=details,
        user_id=user_id,
        ip_address=ip_address,
        resource_type=resource_type,
        resource_id=resource_id
    )
    db.add(audit)
    db.commit()

