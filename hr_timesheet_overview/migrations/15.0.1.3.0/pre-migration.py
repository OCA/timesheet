# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo.tools import parse_version


@openupgrade.migrate()
def migrate(env, version):
    if parse_version(version) <= parse_version("15.0.1.2.0"):
        openupgrade.logged_query(
            env.cr,
            """DELETE FROM ir_act_window WHERE res_model = 'hr.employee.hour.report';""",
        )
