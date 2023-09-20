"""Refactoring Task

Revision ID: d4756b728e5f
Revises: d2c4c8060b26
Create Date: 2023-09-12 20:57:18.296677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4756b728e5f'
down_revision: Union[str, None] = 'd2c4c8060b26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('task', 'timeframe',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=20),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('task', 'timeframe',
               existing_type=sa.String(length=20),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###