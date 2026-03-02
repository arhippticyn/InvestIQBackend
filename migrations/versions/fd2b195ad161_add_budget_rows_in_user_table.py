"""add budget rows in user table

Revision ID: fd2b195ad161
Revises: b5b0f172b72d
Create Date: 2026-03-02 23:13:35.167213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd2b195ad161'
down_revision: Union[str, Sequence[str], None] = 'b5b0f172b72d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('budget', sa.Integer(), nullable=True, server_default='0'))
    op.execute("UPDATE users SET budget = 0 WHERE budget IS NULL")
    op.alter_column('users', 'budget', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'budget')
