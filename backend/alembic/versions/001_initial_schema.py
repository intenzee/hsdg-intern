"""Initial schema for CA Firm MIS

Revision ID: 001
Revises: 
Create Date: 2026-08-11 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('pan', sa.String(length=10), nullable=True),
        sa.Column('gstin', sa.String(length=15), nullable=True),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('partner_in_charge', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
    op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=False)
    op.create_index(op.f('ix_clients_pan'), 'clients', ['pan'], unique=True)
    op.create_index(op.f('ix_clients_gstin'), 'clients', ['gstin'], unique=True)

    # Create compliance_tasks table
    op.create_table(
        'compliance_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(length=100), nullable=False),
        sa.Column('period_label', sa.String(length=50), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('assignee', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_tasks_id'), 'compliance_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_compliance_tasks_client_id'), 'compliance_tasks', ['client_id'], unique=False)
    op.create_index(op.f('ix_compliance_tasks_task_type'), 'compliance_tasks', ['task_type'], unique=False)
    op.create_index(op.f('ix_compliance_tasks_due_date'), 'compliance_tasks', ['due_date'], unique=False)
    op.create_index(op.f('ix_compliance_tasks_assignee'), 'compliance_tasks', ['assignee'], unique=False)
    op.create_index(op.f('ix_compliance_tasks_status'), 'compliance_tasks', ['status'], unique=False)

    # Create task_documents table
    op.create_table(
        'task_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('is_received', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['compliance_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_documents_id'), 'task_documents', ['id'], unique=False)
    op.create_index(op.f('ix_task_documents_task_id'), 'task_documents', ['task_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_task_documents_task_id'), table_name='task_documents')
    op.drop_index(op.f('ix_task_documents_id'), table_name='task_documents')
    op.drop_table('task_documents')
    
    op.drop_index(op.f('ix_compliance_tasks_status'), table_name='compliance_tasks')
    op.drop_index(op.f('ix_compliance_tasks_assignee'), table_name='compliance_tasks')
    op.drop_index(op.f('ix_compliance_tasks_due_date'), table_name='compliance_tasks')
    op.drop_index(op.f('ix_compliance_tasks_task_type'), table_name='compliance_tasks')
    op.drop_index(op.f('ix_compliance_tasks_client_id'), table_name='compliance_tasks')
    op.drop_index(op.f('ix_compliance_tasks_id'), table_name='compliance_tasks')
    op.drop_table('compliance_tasks')
    
    op.drop_index(op.f('ix_clients_gstin'), table_name='clients')
    op.drop_index(op.f('ix_clients_pan'), table_name='clients')
    op.drop_index(op.f('ix_clients_name'), table_name='clients')
    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_table('clients')
