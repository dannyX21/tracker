"""Add user table fields.

Revision ID: 360c7c7dfc93
Revises: f6a5dcf31355
Create Date: 2016-07-08 13:59:55.844062

"""

# revision identifiers, used by Alembic.
revision = '360c7c7dfc93'
down_revision = 'f6a5dcf31355'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('member_since', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('name', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('position', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'position')
    op.drop_column('users', 'name')
    op.drop_column('users', 'member_since')
    op.drop_column('users', 'last_seen')
    ### end Alembic commands ###
