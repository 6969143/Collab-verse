"""
add notifications table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'notif001'
down_revision = '20686dd323f1'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id'), nullable=True),
        sa.Column('message', sa.String(255), nullable=False),
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('notification') 