"""Multi-agent investigation

Revision ID: def012345678
Revises: bcdef0123456
Create Date: 2026-09-15 10:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'def012345678'
down_revision: Union[str, None] = 'bcdef0123456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Update Enum InvestigationStatus
    # Since we are likely in a dev environment and want to avoid complex alter type,
    # we drop ai_investigations and its dependents (since this is an AI overhaul).
    op.execute('DROP TABLE IF EXISTS ai_actions CASCADE')
    op.execute('DROP TABLE IF EXISTS problem_clarifications CASCADE')
    op.execute('DROP TABLE IF EXISTS ai_findings CASCADE')
    op.execute('DROP TABLE IF EXISTS ai_messages CASCADE')
    op.execute('DROP TABLE IF EXISTS ai_critic_reviews CASCADE')
    op.execute('DROP TABLE IF EXISTS ai_proposed_solutions CASCADE')
    op.execute('DROP TABLE IF EXISTS ai_investigations CASCADE')
    op.execute('DROP TYPE IF EXISTS investigationstatus CASCADE')

    investigation_status = postgresql.ENUM('CREATED', 'ANALYZING', 'WAITING_FOR_USER', 'RESEARCHING', 'DIAGNOSING', 'GENERATING', 'REVIEWING', 'READY', 'VERIFYING', 'COMPLETED', 'FAILED', name='investigationstatus', create_type=False)
    investigation_status.create(op.get_bind())

    # 2. Create AIInvestigation
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

    # 3. Create AIFinding
    op.create_table('ai_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('finding', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['investigation_id'], ['ai_investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Create AIProposedSolution
    op.create_table('ai_proposed_solutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['investigation_id'], ['ai_investigations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Create AICriticReview
    op.create_table('ai_critic_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_safe', sa.Boolean(), nullable=False),
        sa.Column('missing_evidence', sa.JSON(), nullable=True),
        sa.Column('contradictions', sa.JSON(), nullable=True),
        sa.Column('unsafe_instructions', sa.JSON(), nullable=True),
        sa.Column('weak_assumptions', sa.JSON(), nullable=True),
        sa.Column('alternative_explanations', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['solution_id'], ['ai_proposed_solutions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('solution_id')
    )

    # 6. Recreate ProblemClarification
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

    # 7. Recreate AIAction
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

    # 8. Recreate AIMessage
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
    pass # In dev, we can just rebuild the database.


