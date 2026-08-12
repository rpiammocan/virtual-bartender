from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.exporter import recipe_to_markdown, recipe_to_text

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/recipe/{recipe_id}.md")
def export_recipe_markdown(recipe_id: int, db: Session = Depends(get_db)):
    try:
        content = recipe_to_markdown(db, recipe_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="recipe-{recipe_id}.md"'},
    )


@router.get("/recipe/{recipe_id}.txt")
def export_recipe_text(recipe_id: int, db: Session = Depends(get_db)):
    try:
        content = recipe_to_text(db, recipe_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="recipe-{recipe_id}.txt"'},
    )
