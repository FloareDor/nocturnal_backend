""" "2"

Revision ID: 54dcc4403c92
Revises: d8feca8c9a8a
Create Date: 2024-08-29 22:52:39.813557

"""


from alembic import op

# revision identifiers, used by Alembic.
revision = "54dcc4403c92"
down_revision = "d8feca8c9a8a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "bar_reports", ["id"])
    op.create_unique_constraint(None, "posts", ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "posts", type_="unique")
    op.drop_constraint(None, "bar_reports", type_="unique")
    # ### end Alembic commands ###
