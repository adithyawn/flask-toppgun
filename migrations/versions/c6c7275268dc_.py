"""empty message

Revision ID: c6c7275268dc
Revises: 938cf7b9f718
Create Date: 2020-12-13 23:13:26.148106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6c7275268dc'
down_revision = '938cf7b9f718'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'post', 'jenis_toppgun', ['post_jenis_toppgun'], ['id_jenis_toppgun'])
    op.create_foreign_key(None, 'post', 'kategori_lean', ['post_kategori_lean'], ['id_kategori_lean'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.drop_constraint(None, 'post', type_='foreignkey')
    # ### end Alembic commands ###
