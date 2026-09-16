"""Update notification model

Revision ID: bcdef1234567
Revises: abcde1234567
Create Date: 2026-09-15 10:57:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bcdef1234567'
down_revision: Union[str, None] = 'abcde1234567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('notifications', sa.Column('type', sa.String(), nullable=True))
    op.add_column('notifications', sa.Column('body', sa.Text(), nullable=True))
    op.add_column('notifications', sa.Column('entity_type', sa.String(), nullable=True))
    op.add_column('notifications', sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('notifications', sa.Column('read_at', sa.DateTime(timezone=True), nullable=True))
    
    # Backfill
    op.execute("UPDATE notifications SET type = 'SYSTEM', body = message")
    op.execute("UPDATE notifications SET read_at = now() WHERE is_read = true")
    
    op.alter_column('notifications', 'type', nullable=False)
    op.alter_column('notifications', 'body', nullable=False)
    
    op.drop_column('notifications', 'message')
    op.drop_column('notifications', 'is_read')


def downgrade() -> None:
    pass

