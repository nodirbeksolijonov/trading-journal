"""Add fees, split trade_date into entry_date and exit_date.

Existing closed trades get exit_date = entry_date, since they were logged with a single date.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("trades") as batch:
        batch.drop_index("ix_trades_trade_date")
        batch.alter_column("trade_date", new_column_name="entry_date")
        batch.add_column(sa.Column("exit_date", sa.Date()))
        batch.add_column(sa.Column("fees", sa.Float(), nullable=False, server_default="0"))

    # Outside the batch: batch mode can't index a column renamed in the same batch.
    op.create_index("ix_trades_entry_date", "trades", ["entry_date"])
    op.create_index("ix_trades_exit_date", "trades", ["exit_date"])
    op.execute("UPDATE trades SET exit_date = entry_date WHERE exit_price IS NOT NULL")


def downgrade() -> None:
    op.drop_index("ix_trades_exit_date", "trades")
    op.drop_index("ix_trades_entry_date", "trades")
    with op.batch_alter_table("trades") as batch:
        batch.drop_column("fees")
        batch.drop_column("exit_date")
        batch.alter_column("entry_date", new_column_name="trade_date")
    op.create_index("ix_trades_trade_date", "trades", ["trade_date"])
