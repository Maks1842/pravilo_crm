"""Refactoring dir_credit

Revision ID: 7ca69f6c4853
Revises: d14bcf6b0527
Create Date: 2023-09-24 12:54:28.440584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ca69f6c4853'
down_revision: Union[str, None] = 'd14bcf6b0527'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('docs_folder', sa.Column('dir_credit_id', sa.Integer(), nullable=True))
    op.drop_constraint('docs_folder_credit_dir_id_fkey', 'docs_folder', type_='foreignkey')
    op.create_foreign_key(None, 'docs_folder', 'dir_credit', ['dir_credit_id'], ['id'])
    op.drop_column('docs_folder', 'credit_dir_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('docs_folder', sa.Column('credit_dir_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'docs_folder', type_='foreignkey')
    op.create_foreign_key('docs_folder_credit_dir_id_fkey', 'docs_folder', 'dir_credit', ['credit_dir_id'], ['id'])
    op.drop_column('docs_folder', 'dir_credit_id')
    # ### end Alembic commands ###
