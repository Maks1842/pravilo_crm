"""Legal_work

Revision ID: c7742871da35
Revises: c48f7970f292
Create Date: 2023-08-17 22:38:42.129659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7742871da35'
down_revision: Union[str, None] = 'c48f7970f292'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bankrupt_cases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number_case', sa.String(length=50), nullable=True),
    sa.Column('date_decision', sa.DATE(), nullable=False),
    sa.Column('date_kommersant', sa.String(length=50), nullable=True),
    sa.Column('date_meeting', sa.String(length=50), nullable=True),
    sa.Column('date_add_registry', sa.DATE(), nullable=True),
    sa.Column('date_sale_property', sa.DATE(), nullable=True),
    sa.Column('tribunal_id', sa.Integer(), nullable=True),
    sa.Column('financial_manager_id', sa.Integer(), nullable=True),
    sa.Column('comment', sa.String(length=200), nullable=True),
    sa.Column('credit_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['credit_id'], ['credit.id'], ),
    sa.ForeignKeyConstraint(['financial_manager_id'], ['ref_financial_manager.id'], ),
    sa.ForeignKeyConstraint(['tribunal_id'], ['ref_tribunal.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('legal_work',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('legal_number', sa.String(length=15), nullable=False),
    sa.Column('legal_section_id', sa.Integer(), nullable=True),
    sa.Column('duplicate_case', sa.String(length=10), nullable=True),
    sa.Column('number_case_1', sa.String(length=50), nullable=True),
    sa.Column('name_task_id', sa.Integer(), nullable=True),
    sa.Column('date_session_1', sa.DATE(), nullable=True),
    sa.Column('date_result_1', sa.DATE(), nullable=True),
    sa.Column('result_1_id', sa.Integer(), nullable=True),
    sa.Column('date_entry_force', sa.DATE(), nullable=True),
    sa.Column('tribunal_1_id', sa.Integer(), nullable=True),
    sa.Column('summa_claim', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('date_incoming_ed', sa.DATE(), nullable=True),
    sa.Column('date_stop_case', sa.DATE(), nullable=True),
    sa.Column('summa_state_duty_claim', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('summa_state_duty_result', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('number_case_2', sa.String(length=50), nullable=True),
    sa.Column('date_session_2', sa.DATE(), nullable=True),
    sa.Column('date_result_2', sa.DATE(), nullable=True),
    sa.Column('result_2_id', sa.Integer(), nullable=True),
    sa.Column('tribunal_2_id', sa.Integer(), nullable=True),
    sa.Column('date_cancel_result', sa.DATE(), nullable=True),
    sa.Column('summa_result_2', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('date_court_costs', sa.DATE(), nullable=True),
    sa.Column('result_court_costs_id', sa.Integer(), nullable=True),
    sa.Column('number_ed', sa.String(length=50), nullable=True),
    sa.Column('date_ed', sa.DATE(), nullable=True),
    sa.Column('summa_ed', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('date_collection', sa.DATE(), nullable=True),
    sa.Column('number_contract', sa.String(length=50), nullable=True),
    sa.Column('date_contract', sa.DATE(), nullable=True),
    sa.Column('comment', sa.String(length=200), nullable=True),
    sa.Column('credit_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['credit_id'], ['credit.id'], ),
    sa.ForeignKeyConstraint(['legal_section_id'], ['ref_legal_section.id'], ),
    sa.ForeignKeyConstraint(['name_task_id'], ['ref_task.id'], ),
    sa.ForeignKeyConstraint(['result_1_id'], ['ref_result_statement.id'], ),
    sa.ForeignKeyConstraint(['result_2_id'], ['ref_result_statement.id'], ),
    sa.ForeignKeyConstraint(['result_court_costs_id'], ['ref_result_statement.id'], ),
    sa.ForeignKeyConstraint(['tribunal_1_id'], ['ref_tribunal.id'], ),
    sa.ForeignKeyConstraint(['tribunal_2_id'], ['ref_tribunal.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('legal_number')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('legal_work')
    op.drop_table('bankrupt_cases')
    # ### end Alembic commands ###
