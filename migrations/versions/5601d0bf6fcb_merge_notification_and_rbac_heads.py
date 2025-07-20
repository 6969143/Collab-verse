"""merge notification and rbac heads

Revision ID: 5601d0bf6fcb
Revises: cc70a80783b7, notif001
Create Date: 2025-07-20 14:32:00.789218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5601d0bf6fcb'
down_revision = ('cc70a80783b7', 'notif001')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
