"""collection_debt refactor 01092023

Revision ID: f62f9d32a553
Revises: ee2e2757c2d0
Create Date: 2023-09-01 16:03:40.960837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f62f9d32a553'
down_revision: Union[str, None] = 'ee2e2757c2d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('collection_debt', sa.Column('type_department_id', sa.Integer(), nullable=False))
    op.drop_constraint('collection_debt_department_presentation_id_fkey', 'collection_debt', type_='foreignkey')
    op.create_foreign_key(None, 'collection_debt', 'ref_type_department', ['type_department_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'collection_debt', type_='foreignkey')
    op.create_foreign_key('collection_debt_department_presentation_id_fkey', 'collection_debt', 'department_presentation', ['department_presentation_id'], ['id'])
    op.drop_column('collection_debt', 'type_department_id')
    # ### end Alembic commands ###
