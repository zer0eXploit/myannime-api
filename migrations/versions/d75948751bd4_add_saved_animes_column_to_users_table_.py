"""Add saved_animes column to users table and create user_animes table

Revision ID: d75948751bd4
Revises: 0b099ed4a0cd
Create Date: 2021-01-17 17:01:47.265592

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd75948751bd4'
down_revision = '0b099ed4a0cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_animes',
    sa.Column('anime_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['anime_id'], ['anime_info.anime_id'], name=op.f('fk_user_animes_anime_id_anime_info')),
    sa.ForeignKeyConstraint(['user_id'], ['users._id'], name=op.f('fk_user_animes_user_id_users'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_animes')
    # ### end Alembic commands ###
