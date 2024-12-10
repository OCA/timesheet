# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo.tools import parse_version


@openupgrade.migrate()
def migrate(env, version):
    if parse_version(version) == parse_version("15.0.1.0.0"):
        openupgrade.logged_query(
            env.cr,
            """ALTER TABLE hr_employee_hour ADD COLUMN IF NOT EXISTS name_id VARCHAR;""",
        )
        openupgrade.logged_query(
            env.cr, """DROP VIEW IF EXISTS hr_employee_hour_report;"""
        )
        openupgrade.logged_query(
            env.cr, """ALTER TABLE hr_employee_hour DROP COLUMN IF EXISTS name;"""
        )
        openupgrade.logged_query(
            env.cr,
            """
UPDATE hr_employee_hour
SET name_id = CONCAT(im.model, ',', res_id)
FROM ir_model AS im
WHERE model_id = im.id;
""",
        )
