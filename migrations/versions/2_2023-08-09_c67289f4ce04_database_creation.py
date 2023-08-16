"""Database creation

Revision ID: c67289f4ce04
Revises: 
Create Date: 2023-08-09 15:51:51.077635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c67289f4ce04'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('departments',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
    )
    op.create_table('roles',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
    )
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=20), nullable=False),
                    sa.Column('password', sa.String(length=15), nullable=False),
                    sa.Column('is_superuser', sa.Boolean(), nullable=True),
                    sa.Column('last_name', sa.String(), nullable=False),
                    sa.Column('first_name', sa.String(), nullable=False),
                    sa.Column('second_name', sa.String(), nullable=True),
                    sa.Column('birthday', sa.TIMESTAMP(), nullable=True),
                    sa.Column('date_joined', sa.TIMESTAMP(), nullable=True),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('username')
    )
    op.create_table('profiles',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('department_id', sa.Integer(), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profiles')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('departments')
    # ### end Alembic commands ###
