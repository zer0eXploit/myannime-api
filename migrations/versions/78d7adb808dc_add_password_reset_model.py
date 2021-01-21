"""Add password reset model

Revision ID: 78d7adb808dc
Revises: c6cc50d52a2f
Create Date: 2021-01-21 15:03:10.677864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78d7adb808dc'
down_revision = 'c6cc50d52a2f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('password_resets',
    sa.Column('password_reset_id', sa.String(length=50), nullable=False),
    sa.Column('expires_at', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users._id'], name=op.f('fk_password_resets_user_id_users')),
    sa.PrimaryKeyConstraint('password_reset_id', name=op.f('pk_password_resets'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('password_resets')
    # ### end Alembic commands ###
