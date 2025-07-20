"""
add applicant_id and application_id to notification
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'notif002'
down_revision = '5601d0bf6fcb'
branch_labels = None
depends_on = None

def upgrade():
    print('--- Running batch alter for notification table ---')
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('applicant_id', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('application_id', sa.Integer, nullable=True))
    print('--- Batch alter complete ---')

def downgrade():
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_column('applicant_id')
        batch_op.drop_column('application_id') 