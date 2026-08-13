from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.services.backup_scheduler import start_backup_scheduler

from app.database import Base, SessionLocal, engine
from app.seed import seed_builtin_data
import app.models  # noqa: F401
from app.api import admin, backups, bars, display, exports, favorites, history, importer, ingredients, inventory, matching, recipes, shopping, shopping_suggestions, surprise

app = FastAPI(
    title="Virtual Bartender API",
    version="1.0.0",
    description="Offline-first virtual bartender backend.",
)

Path(settings.media_path).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_path), name="media")

Base.metadata.create_all(bind=engine)

# Idempotently populate/upgrade the built-in catalog on every startup. Existing
# user-created recipes and inventory remain untouched.
with SessionLocal() as db:
    seed_builtin_data(db)

app.include_router(ingredients.router)
app.include_router(inventory.router)
app.include_router(recipes.router)
app.include_router(bars.router)
app.include_router(shopping.router)
app.include_router(matching.router)
app.include_router(favorites.router)
app.include_router(history.router)
app.include_router(surprise.router)
app.include_router(shopping_suggestions.router)
app.include_router(importer.router)
app.include_router(exports.router)
app.include_router(backups.router)
app.include_router(display.router)
app.include_router(admin.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


start_backup_scheduler()
