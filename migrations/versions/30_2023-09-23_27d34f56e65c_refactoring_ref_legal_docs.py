"""Refactoring ref_legal_docs

Revision ID: 27d34f56e65c
Revises: c47919f9ea7f
Create Date: 2023-09-23 14:44:35.951589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27d34f56e65c'
down_revision: Union[str, None] = 'c47919f9ea7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ref_legal_docs', sa.Column('type_statement_id', sa.Integer(), nullable=True))
    op.add_column('ref_legal_docs', sa.Column('result_statement_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'ref_legal_docs', 'ref_result_statement', ['result_statement_id'], ['id'])
    op.create_foreign_key(None, 'ref_legal_docs', 'ref_type_statement', ['type_statement_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ref_legal_docs', type_='foreignkey')
    op.drop_constraint(None, 'ref_legal_docs', type_='foreignkey')
    op.drop_column('ref_legal_docs', 'result_statement_id')
    op.drop_column('ref_legal_docs', 'type_statement_id')
    # ### end Alembic commands ###
