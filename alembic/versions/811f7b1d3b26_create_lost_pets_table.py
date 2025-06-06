"""Create lost_pets table

Revision ID: 811f7b1d3b26
Revises: 68816d870fa6
Create Date: 2025-03-05 22:45:56.038920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '811f7b1d3b26'
down_revision: Union[str, None] = '68816d870fa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lost_pets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pet_id', sa.Integer(), nullable=False),
    sa.Column('last_seen_location', sa.String(length=255), nullable=False),
    sa.Column('last_seen_date', sa.DateTime(), nullable=False),
    sa.Column('additional_details', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('REPORTED', 'SEARCHING', 'FOUND', 'RESOLVED', name='lostpetstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lost_pets_id'), 'lost_pets', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_lost_pets_id'), table_name='lost_pets')
    op.drop_table('lost_pets')
    # ### end Alembic commands ###
