"""Add token denylist

Revision ID: def123456789
Revises: cdef12345678
Create Date: 2026-09-15 11:14:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'def123456789'
down_revision: Union[str, None] = 'cdef12345678'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('token_denylist',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_denylist_token'), 'token_denylist', ['token'], unique=True)

def downgrade() -> None:
    pass

