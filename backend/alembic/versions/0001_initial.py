"""Initial trades table, as created by the MVP before migrations existed.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("side", sa.String(5), nullable=False),
        sa.Column("entry_price", sa.Float(), nullable=False),
        sa.Column("exit_price", sa.Float()),
        sa.Column("position_size", sa.Float(), nullable=False),
        sa.Column("stop_loss", sa.Float()),
        sa.Column("take_profit", sa.Float()),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("strategy", sa.String(50)),
        sa.Column("notes", sa.Text()),
        sa.Column("emotion_before", sa.String(30)),
        sa.Column("emotion_after", sa.String(30)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_trades_symbol", "trades", ["symbol"])
    op.create_index("ix_trades_trade_date", "trades", ["trade_date"])
    op.create_index("ix_trades_strategy", "trades", ["strategy"])


def downgrade() -> None:
    op.drop_table("trades")
