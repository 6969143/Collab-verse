"""merge heads

Revision ID: 20686dd323f1
Revises: add_labels_to_projects, add_profile_fields
Create Date: 2025-07-13 16:05:44.895153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20686dd323f1'
down_revision = ('add_labels_to_projects', 'add_profile_fields')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
