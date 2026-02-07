"""Initial database schema for petrol pump ledger automation

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-14 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('pump_name', sa.String(), nullable=True),
        sa.Column('pump_location', sa.String(), nullable=True),
        sa.Column('language_preference', sa.String(), nullable=True, server_default='en'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)

    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language_preference', sa.String(), nullable=True, server_default='en'),
        sa.Column('report_layout', sa.String(), nullable=True, server_default='standard'),
        sa.Column('date_format', sa.String(), nullable=True, server_default='DD-MM-YYYY'),
        sa.Column('unit_preference', sa.String(), nullable=True, server_default='liters'),
        sa.Column('currency_symbol', sa.String(), nullable=True, server_default='₨'),
        sa.Column('custom_column_order', sa.Text(), nullable=True),
        sa.Column('enable_urdu_translation', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('enable_email_notifications', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('enable_sms_notifications', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('custom_report_templates', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_id'), 'user_preferences', ['id'], unique=False)

    # Create ledger_pages table
    op.create_table('ledger_pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('original_image_url', sa.String(), nullable=False),
        sa.Column('processed_image_url', sa.String(), nullable=True),
        sa.Column('processing_status', sa.String(), nullable=True, server_default='pending'),
        sa.Column('processing_errors', sa.Text(), nullable=True),
        sa.Column('upload_date', sa.DateTime(), nullable=True),
        sa.Column('processed_date', sa.DateTime(), nullable=True),
        sa.Column('ocr_confidence_score', sa.Float(), nullable=True),
        sa.Column('detected_columns', sa.Text(), nullable=True),
        sa.Column('extracted_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ledger_pages_id'), 'ledger_pages', ['id'], unique=False)

    # Create sales_entries table
    op.create_table('sales_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ledger_page_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('nozzle_id', sa.String(), nullable=True),
        sa.Column('fuel_type', sa.String(), nullable=True),
        sa.Column('opening_reading', sa.Float(), nullable=True),
        sa.Column('closing_reading', sa.Float(), nullable=True),
        sa.Column('liters_sold', sa.Float(), nullable=True),
        sa.Column('rate_per_liter', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('ocr_confidence', sa.Float(), nullable=True),
        sa.Column('is_manual_correction', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('manual_correction_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ledger_page_id'], ['ledger_pages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_entries_id'), 'sales_entries', ['id'], unique=False)

    # Create daily_reports table
    op.create_table('daily_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.DateTime(), nullable=False),
        sa.Column('total_liters_petrol', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_liters_diesel', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_liters_cng', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_revenue_petrol', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_revenue_diesel', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_revenue_cng', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_nozzles_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_sales_entries', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('grand_total_liters', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('grand_total_revenue', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('export_format', sa.String(), nullable=True, server_default='json'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_reports_id'), 'daily_reports', ['id'], unique=False)

    # Create monthly_reports table
    op.create_table('monthly_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('month_year', sa.String(), nullable=False),
        sa.Column('total_liters_petrol', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_liters_diesel', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_liters_cng', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_revenue_petrol', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_revenue_diesel', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_revenue_cng', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('avg_daily_liters', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('avg_daily_revenue', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('peak_sales_day', sa.DateTime(), nullable=True),
        sa.Column('peak_sales_amount', sa.Float(), nullable=True),
        sa.Column('total_operational_days', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_daily_reports', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('trend_indicator', sa.String(), nullable=True, server_default='neutral'),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('export_format', sa.String(), nullable=True, server_default='json'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monthly_reports_id'), 'monthly_reports', ['id'], unique=False)

    # Create column_definitions table
    op.create_table('column_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ledger_page_id', sa.Integer(), nullable=False),
        sa.Column('column_name', sa.String(), nullable=False),
        sa.Column('column_type', sa.String(), nullable=False),
        sa.Column('position_order', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('is_manual_override', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('manual_definition_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ledger_page_id'], ['ledger_pages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_column_definitions_id'), 'column_definitions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('column_definitions')
    op.drop_table('monthly_reports')
    op.drop_table('daily_reports')
    op.drop_table('sales_entries')
    op.drop_table('ledger_pages')
    op.drop_table('user_preferences')
    op.drop_table('users')