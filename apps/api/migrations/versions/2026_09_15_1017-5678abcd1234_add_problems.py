"""Add problems

Revision ID: 5678abcd1234
Revises: 1234abcd5678
Create Date: 2026-09-15 10:17:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5678abcd1234'
down_revision: Union[str, None] = '1234abcd5678'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # problem_categories
    op.create_table('problem_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_problem_categories_name'), 'problem_categories', ['name'], unique=True)

    # tags
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)

    # create enum type
    problem_status = postgresql.ENUM('DRAFT', 'AI_PROCESSING', 'OPEN', 'SOLVED', 'CLOSED', name='problemstatus', create_type=False)
    problem_status.create(op.get_bind())

    # problems
    op.create_table('problems',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('public_id', sa.String(), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', problem_status, nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('urgency', sa.String(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('solved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['problem_categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_problems_public_id'), 'problems', ['public_id'], unique=True)

    # problem_tags
    op.create_table('problem_tags',
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('problem_id', 'tag_id')
    )

    # problem_files
    op.create_table('problem_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('problem_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('problem_files')
    op.drop_table('problem_tags')
    op.drop_index(op.f('ix_problems_public_id'), table_name='problems')
    op.drop_table('problems')
    
    problem_status = postgresql.ENUM('DRAFT', 'AI_PROCESSING', 'OPEN', 'SOLVED', 'CLOSED', name='problemstatus', create_type=False)
    problem_status.drop(op.get_bind())
    
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_problem_categories_name'), table_name='problem_categories')
    op.drop_table('problem_categories')

