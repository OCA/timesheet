# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo.tools.sql import column_exists

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    if not column_exists(env.cr, "account_analytic_line", "day_week"):
        logger.info("Creating field day_week on account_analytic_line")
        env.cr.execute(
            """
            ALTER TABLE account_analytic_line
            ADD COLUMN day_week character varying
            """
        )
    logger.info("Updating field day_week for account_analytic_line records")
    env.cr.execute(
        """
        UPDATE account_analytic_line
        SET day_week = (
            CASE DATE_PART('dow', date)
            WHEN 0 THEN 6
            ELSE DATE_PART('dow', date) - 1
        END)::character varying
        """
    )
