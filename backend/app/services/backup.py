import json
import shutil
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models import BackupRecord


BACKUP_VERSION = 1


def _sqlite_path() -> Path:
    prefix = "sqlite:///"
    if not settings.database_url.startswith(prefix):
        raise ValueError("Automatic backup currently supports SQLite only")
    raw = settings.database_url[len(prefix):]
    return Path(raw).resolve()


def _backup_dir() -> Path:
    path = Path(settings.backups_path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_backup(db: Session, reason: str = "manual") -> dict:
    database_path = _sqlite_path()
    if not database_path.exists():
        raise FileNotFoundError("Database file not found")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = _backup_dir()
    work_db = backup_dir / f"bartender-{stamp}.db"
    zip_path = backup_dir / f"virtual-bartender-backup-v{BACKUP_VERSION}-{stamp}.zip"

    # SQLite online backup API avoids copying a live database file unsafely.
    source = sqlite3.connect(database_path)
    dest = sqlite3.connect(work_db)
    try:
        source.backup(dest)
    finally:
        dest.close()
        source.close()

    manifest = {
        "backup_version": BACKUP_VERSION,
        "created_at": datetime.now().isoformat(),
        "reason": reason,
        "database_filename": work_db.name,
    }
    manifest_path = backup_dir / f"manifest-{stamp}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(work_db, work_db.name)
        z.write(manifest_path, "manifest.json")

    size = zip_path.stat().st_size
    work_db.unlink(missing_ok=True)
    manifest_path.unlink(missing_ok=True)

    record = BackupRecord(
        path=str(zip_path),
        size_bytes=size,
        status="complete",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    prune_backups(db)

    return {
        "id": record.id,
        "path": str(zip_path),
        "size_bytes": size,
        "status": "complete",
    }


def list_backups(db: Session) -> list[BackupRecord]:
    return (
        db.query(BackupRecord)
        .order_by(BackupRecord.created_at.desc())
        .all()
    )


def prune_backups(db: Session) -> None:
    keep = 10
    rows = list_backups(db)
    for row in rows[keep:]:
        try:
            Path(row.path).unlink(missing_ok=True)
        except Exception:
            pass
        db.delete(row)
    db.commit()


def restore_backup(db: Session, backup_id: int) -> dict:
    record = db.get(BackupRecord, backup_id)
    if not record:
        raise FileNotFoundError("Backup record not found")

    zip_path = Path(record.path)
    if not zip_path.exists():
        raise FileNotFoundError("Backup file not found")

    database_path = _sqlite_path()
    temp_dir = _backup_dir() / f"restore-{backup_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(temp_dir)

    manifest_path = temp_dir / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("Backup manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest.get("backup_version") != BACKUP_VERSION:
        raise ValueError("Unsupported backup version")

    backup_db = temp_dir / manifest["database_filename"]
    if not backup_db.exists():
        raise ValueError("Database payload missing")

    # Make a safety backup of the current state before replacing it.
    safety = database_path.with_suffix(".pre-restore.db")
    if database_path.exists():
        shutil.copy2(database_path, safety)

    shutil.copy2(backup_db, database_path)
    shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "status": "restored",
        "backup_id": backup_id,
        "safety_copy": str(safety),
    }
