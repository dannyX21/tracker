"""add subscription table.

Revision ID: 9ba5b6952791
Revises: d6211be97a78
Create Date: 2016-07-15 23:04:14.510496

"""

# revision identifiers, used by Alembic.
revision = '9ba5b6952791'
down_revision = 'd6211be97a78'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscriptions',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('po_line_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['po_line_id'], ['pos.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'po_line_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscriptions')
    ### end Alembic commands ###
