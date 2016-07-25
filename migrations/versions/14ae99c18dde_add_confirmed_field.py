"""Add confirmed field

Revision ID: 14ae99c18dde
Revises: 110c1fd98ea9
Create Date: 2016-07-07 16:29:18.039774

"""

# revision identifiers, used by Alembic.
revision = '14ae99c18dde'
down_revision = '110c1fd98ea9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    ### end Alembic commands ###
