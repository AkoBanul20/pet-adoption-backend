"""remove default value for 'deleted_at'

Revision ID: e6a8a5cc3a1d
Revises: 5eb93c28fb4f
Create Date: 2025-03-07 20:55:25.527144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6a8a5cc3a1d'
down_revision: Union[str, None] = '5eb93c28fb4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
