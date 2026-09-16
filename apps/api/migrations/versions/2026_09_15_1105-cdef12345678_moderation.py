"""Add moderation models

Revision ID: cdef12345678
Revises: bcdef1234567
Create Date: 2026-09-15 11:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cdef12345678'
down_revision: Union[str, None] = 'bcdef1234567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add columns to problems and solutions
    op.add_column('problems', sa.Column('is_hidden', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('problems', sa.Column('is_locked', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('solutions', sa.Column('is_hidden', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('solutions', sa.Column('is_locked', sa.Boolean(), server_default='false', nullable=False))
    
    # Create moderation_actions table
    op.create_table('moderation_actions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('moderator_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('entity_type', sa.String(), nullable=False),
    sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('target_user_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create reports table
    op.create_table('reports',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('reporter_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('entity_type', sa.String(), nullable=False),
    sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('reason', sa.String(), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create content_flags
    op.create_table('content_flags',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('entity_type', sa.String(), nullable=False),
    sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('risk_level', sa.String(), nullable=False),
    sa.Column('flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_restrictions
    op.create_table('user_restrictions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('restriction_type', sa.String(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    pass

