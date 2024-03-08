# Copyright 2019 Camptocamp SA
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from psycopg2 import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Initialize the value of the given column for existing rows in a fast way."""
    _logger.info(
        "Initializing column `unit_amount_rounded` with the " "value of `unit_amount`"
    )
    table = sql.Identifier("account_analytic_line")
    column = sql.Identifier("unit_amount_rounded")
    cr.execute(  # pylint: disable=E8103
        sql.SQL("ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} NUMERIC").format(
            table, column
        )
    )
    cr.execute(  # pylint: disable=E8103
        sql.SQL(
            "UPDATE {table} SET {column} = unit_amount WHERE {column} IS NULL"
        ).format(table=table, column=column)
    )
