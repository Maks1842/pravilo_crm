"""Refactoring tasks

Revision ID: 007f432f8aeb
Revises: 27d34f56e65c
Create Date: 2023-09-23 15:29:26.408789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007f432f8aeb'
down_revision: Union[str, None] = '27d34f56e65c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('legal_work', sa.Column('legal_docs_id', sa.Integer(), nullable=True))
    op.drop_constraint('legal_work_name_task_id_fkey', 'legal_work', type_='foreignkey')
    op.create_foreign_key(None, 'legal_work', 'ref_legal_docs', ['legal_docs_id'], ['id'])
    op.drop_column('legal_work', 'name_task_id')
    op.drop_constraint('task_name_id_fkey', 'task', type_='foreignkey')
    op.create_foreign_key(None, 'task', 'ref_legal_docs', ['name_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.create_foreign_key('task_name_id_fkey', 'task', 'ref_task', ['name_id'], ['id'])
    op.add_column('legal_work', sa.Column('name_task_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'legal_work', type_='foreignkey')
    op.create_foreign_key('legal_work_name_task_id_fkey', 'legal_work', 'ref_task', ['name_task_id'], ['id'])
    op.drop_column('legal_work', 'legal_docs_id')
    # ### end Alembic commands ###
