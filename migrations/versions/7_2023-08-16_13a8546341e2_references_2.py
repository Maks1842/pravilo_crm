"""References_2

Revision ID: 13a8546341e2
Revises: 9f073962a846
Create Date: 2023-08-16 18:07:06.051820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13a8546341e2'
down_revision: Union[str, None] = '9f073962a846'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ref_legal_section',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ref_section_card_debtor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ref_type_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ref_legal_docs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('section_card_id', sa.Integer(), nullable=True),
    sa.Column('legal_section_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['legal_section_id'], ['ref_legal_section.id'], ),
    sa.ForeignKeyConstraint(['section_card_id'], ['ref_section_card_debtor.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ref_result_statement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('type_statement_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['type_statement_id'], ['ref_type_statement.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ref_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('section_card_id', sa.Integer(), nullable=True),
    sa.Column('legal_doc_id', sa.Integer(), nullable=True),
    sa.Column('result_statement_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['legal_doc_id'], ['ref_legal_docs.id'], ),
    sa.ForeignKeyConstraint(['result_statement_id'], ['ref_result_statement.id'], ),
    sa.ForeignKeyConstraint(['section_card_id'], ['ref_section_card_debtor.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ref_task')
    op.drop_table('ref_result_statement')
    op.drop_table('ref_legal_docs')
    op.drop_table('ref_type_templates')
    op.drop_table('ref_section_card_debtor')
    op.drop_table('ref_legal_section')
    # ### end Alembic commands ###
