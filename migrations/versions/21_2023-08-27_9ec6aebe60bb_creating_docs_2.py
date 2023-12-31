"""creating_docs_2

Revision ID: 9ec6aebe60bb
Revises: 390eacfdc02f
Create Date: 2023-08-27 18:28:19.338239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ec6aebe60bb'
down_revision: Union[str, None] = '390eacfdc02f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('docs_generator_declension', 'tvorit',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
    op.alter_column('docs_generator_declension', 'predl',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
    op.alter_column('registry_headers', 'employ_registry',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('registry_headers', 'employ_registry',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('docs_generator_declension', 'predl',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
    op.alter_column('docs_generator_declension', 'tvorit',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
    # ### end Alembic commands ###
