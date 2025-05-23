"""add new columns for adoption_pet

Revision ID: d1c0087c0e2a
Revises: a6f8e35011c3
Create Date: 2025-04-29 14:41:51.670852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1c0087c0e2a'
down_revision: Union[str, None] = 'a6f8e35011c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('adoption_pets', sa.Column('is_vaccinated', sa.Boolean(), nullable=True))
    op.add_column('adoption_pets', sa.Column('is_neutered', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_adoption_pets_is_neutered'), 'adoption_pets', ['is_neutered'], unique=False)
    op.create_index(op.f('ix_adoption_pets_is_vaccinated'), 'adoption_pets', ['is_vaccinated'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_adoption_pets_is_vaccinated'), table_name='adoption_pets')
    op.drop_index(op.f('ix_adoption_pets_is_neutered'), table_name='adoption_pets')
    op.drop_column('adoption_pets', 'is_neutered')
    op.drop_column('adoption_pets', 'is_vaccinated')
    # ### end Alembic commands ###
