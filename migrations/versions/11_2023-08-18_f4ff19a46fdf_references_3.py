"""references_3

Revision ID: f4ff19a46fdf
Revises: c7742871da35
Create Date: 2023-08-18 17:09:25.600677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4ff19a46fdf'
down_revision: Union[str, None] = 'c7742871da35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ref_bank',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('type_department_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('address_index', sa.String(length=6), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.Column('phone', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('bik', sa.String(length=9), nullable=False),
    sa.Column('inn', sa.String(length=10), nullable=True),
    sa.Column('corr_account', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['region_id'], ['ref_region.id'], ),
    sa.ForeignKeyConstraint(['type_department_id'], ['ref_type_department.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('bik'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ref_pfr',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('type_department_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('address_index', sa.String(length=6), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.Column('phone', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('class_code', sa.String(length=15), nullable=True),
    sa.ForeignKeyConstraint(['region_id'], ['ref_region.id'], ),
    sa.ForeignKeyConstraint(['type_department_id'], ['ref_type_department.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_code'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ref_rosp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('type_department_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('address_index', sa.String(length=6), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.Column('phone', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('class_code', sa.String(length=15), nullable=True),
    sa.ForeignKeyConstraint(['region_id'], ['ref_region.id'], ),
    sa.ForeignKeyConstraint(['type_department_id'], ['ref_type_department.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_code'),
    sa.UniqueConstraint('name')
    )
    op.create_table('department_presentation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('department_presentation_id', sa.Integer(), nullable=False),
    sa.Column('type_department_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['type_department_id'], ['ref_type_department.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('collection_debt', 'department_presentation_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint('collection_debt_department_presentation_id_fkey', 'collection_debt', type_='foreignkey')
    op.drop_constraint('collection_debt_type_department_id_fkey', 'collection_debt', type_='foreignkey')
    op.create_foreign_key(None, 'collection_debt', 'department_presentation', ['department_presentation_id'], ['id'])
    op.drop_column('collection_debt', 'type_department_id')
    op.drop_constraint('executive_productions_rosp_id_fkey', 'executive_productions', type_='foreignkey')
    op.create_foreign_key(None, 'executive_productions', 'ref_rosp', ['rosp_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'executive_productions', type_='foreignkey')
    op.create_foreign_key('executive_productions_rosp_id_fkey', 'executive_productions', 'ref_department_presentation', ['rosp_id'], ['id'])
    op.add_column('collection_debt', sa.Column('type_department_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'collection_debt', type_='foreignkey')
    op.create_foreign_key('collection_debt_type_department_id_fkey', 'collection_debt', 'ref_type_department', ['type_department_id'], ['id'])
    op.create_foreign_key('collection_debt_department_presentation_id_fkey', 'collection_debt', 'ref_department_presentation', ['department_presentation_id'], ['id'])
    op.alter_column('collection_debt', 'department_presentation_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_table('department_presentation')
    op.drop_table('ref_rosp')
    op.drop_table('ref_pfr')
    op.drop_table('ref_bank')
    # ### end Alembic commands ###
