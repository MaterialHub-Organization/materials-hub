"""create dataset_version table

Revision ID: a1b2c3d4e5f6
Revises: c063a020c0c4
Create Date: 2025-12-11 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'c063a020c0c4'
branch_labels = None
depends_on = None


def upgrade():
    # Create dataset_version table
    op.create_table(
        'dataset_version',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('materials_dataset_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('csv_snapshot_path', sa.String(length=512), nullable=False),
        sa.Column('metadata_snapshot', sa.JSON(), nullable=False),
        sa.Column('changelog', sa.JSON(), nullable=True),
        sa.Column('records_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['materials_dataset_id'], ['materials_dataset.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('materials_dataset_id', 'version_number', name='uq_dataset_version')
    )

    # Create index for faster lookups
    op.create_index(
        'idx_dataset_version_lookup',
        'dataset_version',
        ['materials_dataset_id', 'version_number'],
        unique=False
    )


def downgrade():
    # Drop index
    op.drop_index('idx_dataset_version_lookup', table_name='dataset_version')

    # Drop table
    op.drop_table('dataset_version')
