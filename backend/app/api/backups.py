from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.backup import create_backup, list_backups, restore_backup

router = APIRouter(prefix="/api/backups", tags=["backups"])


@router.get("")
def get_backups(db: Session = Depends(get_db)):
    return [
        {
            "id": row.id,
            "path": row.path,
            "created_at": row.created_at,
            "size_bytes": row.size_bytes,
            "status": row.status,
        }
        for row in list_backups(db)
    ]


@router.post("")
def backup_now(db: Session = Depends(get_db)):
    try:
        return create_backup(db, reason="manual")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Backup failed: {exc}")


@router.post("/{backup_id}/restore")
def restore(backup_id: int, db: Session = Depends(get_db)):
    try:
        return restore_backup(db, backup_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Restore failed: {exc}")
