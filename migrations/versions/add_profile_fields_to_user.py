"""add profile fields to user

Revision ID: add_profile_fields
Revises: 4f5fa421dbc5
Create Date: 2025-01-12 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_fields'
down_revision = '4f5fa421dbc5'
branch_labels = None
depends_on = None


def upgrade():
    # Add profile fields to user table
    op.add_column('user', sa.Column('full_name', sa.String(length=150), nullable=True))
    op.add_column('user', sa.Column('job_title', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('department', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('organization', sa.String(length=150), nullable=True))
    op.add_column('user', sa.Column('location', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('avatar_url', sa.String(length=255), nullable=True))


def downgrade():
    # Remove profile fields from user table
    op.drop_column('user', 'avatar_url')
    op.drop_column('user', 'bio')
    op.drop_column('user', 'location')
    op.drop_column('user', 'organization')
    op.drop_column('user', 'department')
    op.drop_column('user', 'job_title')
    op.drop_column('user', 'full_name') 