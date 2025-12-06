"""Add shipping time (hours and minutes) columns to SystemSettings

Revision ID: add_shipping_time_cols
Revises: 2cb824ada633
Create Date: 2025-12-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_shipping_time_cols'
down_revision = '2cb824ada633'
branch_labels = None
depends_on = None


def upgrade():
    # Add hours and minutes columns for Standard Shipping
    op.add_column('system_settings', sa.Column('standard_shipping_hours_min', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('standard_shipping_hours_max', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('standard_shipping_minutes_min', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('standard_shipping_minutes_max', sa.Integer(), nullable=True, server_default='0'))
    
    # Add hours and minutes columns for Express Shipping
    op.add_column('system_settings', sa.Column('express_shipping_hours_min', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('express_shipping_hours_max', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('express_shipping_minutes_min', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('express_shipping_minutes_max', sa.Integer(), nullable=True, server_default='0'))
    
    # Add hours and minutes columns for Free Shipping
    op.add_column('system_settings', sa.Column('free_shipping_hours_min', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('free_shipping_hours_max', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('free_shipping_minutes_min', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('system_settings', sa.Column('free_shipping_minutes_max', sa.Integer(), nullable=True, server_default='0'))


def downgrade():
    # Remove all added columns
    op.drop_column('system_settings', 'free_shipping_minutes_max')
    op.drop_column('system_settings', 'free_shipping_minutes_min')
    op.drop_column('system_settings', 'free_shipping_hours_max')
    op.drop_column('system_settings', 'free_shipping_hours_min')
    
    op.drop_column('system_settings', 'express_shipping_minutes_max')
    op.drop_column('system_settings', 'express_shipping_minutes_min')
    op.drop_column('system_settings', 'express_shipping_hours_max')
    op.drop_column('system_settings', 'express_shipping_hours_min')
    
    op.drop_column('system_settings', 'standard_shipping_minutes_max')
    op.drop_column('system_settings', 'standard_shipping_minutes_min')
    op.drop_column('system_settings', 'standard_shipping_hours_max')
    op.drop_column('system_settings', 'standard_shipping_hours_min')
