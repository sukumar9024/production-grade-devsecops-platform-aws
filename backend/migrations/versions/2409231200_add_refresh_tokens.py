"""Persist revocable refresh tokens.

Revision ID: 2409231200
Revises: 10015957dfba
"""

import sqlalchemy as sa
from alembic import op

revision = "2409231200"
down_revision = "10015957dfba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("jti", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    for column in ("user_id", "jti", "expires_at", "revoked"):
        op.create_index(
            f"ix_refresh_tokens_{column}",
            "refresh_tokens",
            [column],
            unique=column == "jti",
        )


def downgrade() -> None:
    op.drop_table("refresh_tokens")
