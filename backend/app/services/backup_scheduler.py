import threading
import time

from app.database import SessionLocal
from app.services.backup import create_backup

_started = False


def _worker():
    # Daily local backup. The first run waits 24 hours to avoid duplicate startup backups.
    while True:
        time.sleep(24 * 60 * 60)
        db = SessionLocal()
        try:
            create_backup(db, reason="scheduled")
        except Exception:
            pass
        finally:
            db.close()


def start_backup_scheduler():
    global _started
    if _started:
        return
    _started = True
    thread = threading.Thread(target=_worker, daemon=True, name="virtual-bartender-backup")
    thread.start()
