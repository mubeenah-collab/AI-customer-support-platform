"""Add tickets table

Revision ID: 82a1b9c3f4d5
Revises: 71f6e8fbc1b0
Create Date: 2026-08-02 17:22:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82a1b9c3f4d5'
down_revision: Union[str, None] = '71f6e8fbc1b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tickets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickets_user_id'), 'tickets', ['user_id'], unique=False)
    op.create_index(op.f('ix_tickets_status'), 'tickets', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tickets_status'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_user_id'), table_name='tickets')
    op.drop_table('tickets')
