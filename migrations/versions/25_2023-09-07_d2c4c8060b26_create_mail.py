"""Create mail

Revision ID: d2c4c8060b26
Revises: e63c526800bf
Create Date: 2023-09-07 12:18:17.340388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2c4c8060b26'
down_revision: Union[str, None] = 'e63c526800bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mail_in',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sequence_num', sa.Integer(), nullable=False),
    sa.Column('case_number', sa.String(length=100), nullable=True),
    sa.Column('credit_id', sa.Integer(), nullable=True),
    sa.Column('barcode', sa.String(length=20), nullable=True),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('addresser', sa.String(length=200), nullable=False),
    sa.Column('name_doc_id', sa.Integer(), nullable=True),
    sa.Column('resolution_id', sa.Integer(), nullable=True),
    sa.Column('comment', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['credit_id'], ['credit.id'], ),
    sa.ForeignKeyConstraint(['name_doc_id'], ['ref_legal_docs.id'], ),
    sa.ForeignKeyConstraint(['resolution_id'], ['ref_result_statement.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sequence_num')
    )
    op.create_table('mail_out',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sequence_num', sa.Integer(), nullable=False),
    sa.Column('case_number', sa.String(length=100), nullable=True),
    sa.Column('credit_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('name_doc', sa.String(length=200), nullable=False),
    sa.Column('addresser', sa.String(length=200), nullable=False),
    sa.Column('recipient_address', sa.String(length=200), nullable=False),
    sa.Column('mass', sa.Integer(), nullable=True),
    sa.Column('gov_toll', sa.Integer(), nullable=True),
    sa.Column('trek', sa.String(length=20), nullable=True),
    sa.Column('category_mail', sa.String(length=20), nullable=True),
    sa.Column('type_mail', sa.JSON(), nullable=True),
    sa.Column('type_package', sa.String(length=20), nullable=True),
    sa.Column('barcode', sa.String(length=20), nullable=True),
    sa.Column('num_symbol', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('comment', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['credit_id'], ['credit.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sequence_num')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mail_out')
    op.drop_table('mail_in')
    # ### end Alembic commands ###
