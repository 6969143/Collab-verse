"""add labels to projects

NOTE: The task_status enum change for 'testing' is handled in a new migration.

Revision ID: add_labels_to_projects
Revises: 4f5fa421dbc5
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_labels_to_projects'
down_revision = '4f5fa421dbc5'
branch_labels = None
depends_on = None


def upgrade():
    # Create label table
    op.create_table('label',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create project_labels association table
    op.create_table('project_labels',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('label_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['label_id'], ['label.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('project_id', 'label_id')
    )


def downgrade():
    op.drop_table('project_labels')
    op.drop_table('label') 