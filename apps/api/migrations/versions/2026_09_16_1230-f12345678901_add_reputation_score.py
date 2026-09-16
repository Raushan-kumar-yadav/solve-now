"""Add reputation_score to users

Revision ID: f12345678901
Revises: ef1234567890
Create Date: 2026-09-16 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f12345678901'
down_revision: Union[str, None] = 'ef1234567890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('reputation_score', sa.Integer(), nullable=False, server_default='0'))

def downgrade() -> None:
    op.drop_column('users', 'reputation_score')

