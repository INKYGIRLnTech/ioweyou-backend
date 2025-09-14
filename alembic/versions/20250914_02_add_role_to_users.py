"""
add role column to users

Revision ID: 20250914_02
Revises: 20250914_01
Create Date: 2025-09-14
"""

from alembic import op
import sqlalchemy as sa


revision = '20250914_02'
down_revision = '20250914_01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'role')

