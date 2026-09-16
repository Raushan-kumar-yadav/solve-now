"""Add audit log

Revision ID: ef1234567890
Revises: def123456789
Create Date: 2026-09-15 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ef1234567890'
down_revision: Union[str, None] = 'def123456789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('audit_logs', sa.Column('ip_address', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('audit_logs', 'ip_address')
