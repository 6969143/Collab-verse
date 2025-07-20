"""
add application_id to notification
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'notif003'
down_revision = 'notif002'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('application_id', sa.Integer, nullable=True))

def downgrade():
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_column('application_id') 