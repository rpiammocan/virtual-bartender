"""add image metadata and ingredient aliases

Revision ID: 0002_release_prep
Revises:
Create Date: 2026-08-12
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_release_prep"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "ingredient_aliases" not in inspector.get_table_names():
        op.create_table(
            "ingredient_aliases",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("alias", sa.String(length=200), nullable=False),
            sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id"), nullable=False),
            sa.Column("source", sa.String(length=50), nullable=False, server_default="built_in"),
        )
        op.create_index("ix_ingredient_aliases_alias", "ingredient_aliases", ["alias"], unique=True)

    recipe_columns = {c["name"] for c in inspector.get_columns("recipes")}
    with op.batch_alter_table("recipes") as batch:
        if "image_source_url" not in recipe_columns:
            batch.add_column(sa.Column("image_source_url", sa.String(length=2000)))
        if "image_license" not in recipe_columns:
            batch.add_column(sa.Column("image_license", sa.String(length=200)))
        if "image_attribution" not in recipe_columns:
            batch.add_column(sa.Column("image_attribution", sa.String(length=500)))
        if "image_ai_generated" not in recipe_columns:
            batch.add_column(sa.Column("image_ai_generated", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table("recipes") as batch:
        for name in ["image_ai_generated", "image_attribution", "image_license", "image_source_url"]:
            try:
                batch.drop_column(name)
            except Exception:
                pass
    try:
        op.drop_table("ingredient_aliases")
    except Exception:
        pass
