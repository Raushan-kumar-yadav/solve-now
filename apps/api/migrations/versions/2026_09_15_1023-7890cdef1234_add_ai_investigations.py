"""Add AI investigations

Revision ID: 7890cdef1234
Revises: 5678abcd1234
Create Date: 2026-09-15 10:23:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7890cdef1234'
down_revision: Union[str, None] = '5678abcd1234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Enum
    investigation_status = postgresql.ENUM('PENDING', 'PROCESSING', 'NEEDS_CLARIFICATION', 'COMPLETED', 'FAILED', name='investigationstatus', create_type=False)
    investigation_status.create(op.get_bind())

    # ai_investigations
    op.create_table('ai_investigations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', investigation_status, nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('problem_id')
    )

    # ai_findings
    op.create_table('ai_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('subcategory', sa.String(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('urgency', sa.String(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('potential_causes', sa.JSON(), nullable=True),
        sa.Column('missing_information', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['investigation_id'], ['ai_investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('investigation_id')
    )

    # problem_clarifications
    op.create_table('problem_clarifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['investigation_id'], ['ai_investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ai_actions
    op.create_table('ai_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('input_metadata', sa.JSON(), nullable=True),
        sa.Column('output_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['investigation_id'], ['ai_investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ai_messages
    op.create_table('ai_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content_summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['investigation_id'], ['ai_investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('ai_messages')
    op.drop_table('ai_actions')
    op.drop_table('problem_clarifications')
    op.drop_table('ai_findings')
    op.drop_table('ai_investigations')
    
    investigation_status = postgresql.ENUM('PENDING', 'PROCESSING', 'NEEDS_CLARIFICATION', 'COMPLETED', 'FAILED', name='investigationstatus', create_type=False)
    investigation_status.drop(op.get_bind())

