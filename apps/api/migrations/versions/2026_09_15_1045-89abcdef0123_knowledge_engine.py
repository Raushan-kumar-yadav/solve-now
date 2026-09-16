"""Knowledge engine and pgvector

Revision ID: 89abcdef0123
Revises: def012345678
Create Date: 2026-09-15 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '89abcdef0123'
down_revision: Union[str, None] = 'def012345678'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Enable pgvector
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # 2. Add embedding to Problem
    op.add_column('problems', sa.Column('embedding', Vector(768), nullable=True))
    
    # 3. Create Enum
    knowledge_status = postgresql.ENUM('DRAFT', 'PUBLISHED', 'ARCHIVED', 'FLAGGED', name='knowledgestatus', create_type=False)
    knowledge_status.create(op.get_bind())

    # 4. Create KnowledgeDocument
    op.create_table('knowledge_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', knowledge_status, nullable=False),
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('verification_count', sa.Integer(), nullable=True),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['problem_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Create KnowledgeSource
    op.create_table('knowledge_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('knowledge_document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('solution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['knowledge_document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id']),
        sa.ForeignKeyConstraint(['solution_id'], ['solutions.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Create KnowledgeVersion
    op.create_table('knowledge_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('knowledge_document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_diff', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['knowledge_document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    pass

