"""create agreement

Revision ID: 5cf0285fed84
Revises: b0e3fdd21c8f
Create Date: 2023-11-26 16:17:22.690669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cf0285fed84'
down_revision: Union[str, None] = 'b0e3fdd21c8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agreement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('credit_id', sa.Integer(), nullable=True),
    sa.Column('number', sa.String(length=50), nullable=True),
    sa.Column('date', sa.DATE(), nullable=True),
    sa.Column('summa', sa.Integer(), nullable=True),
    sa.Column('payment_schedule', sa.JSON(), nullable=False),
    sa.Column('comment', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['credit_id'], ['credit.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('agreement')
    # ### end Alembic commands ###
