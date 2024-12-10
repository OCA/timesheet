# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo.tools import parse_version


@openupgrade.migrate()
def migrate(env, version):
    if parse_version(version) <= parse_version("15.0.1.1.0"):
        openupgrade.logged_query(
            env.cr,
            """ALTER TABLE hr_employee_hour ADD COLUMN IF NOT EXISTS task_id INTEGER;""",
        )
        openupgrade.logged_query(
            env.cr, """DROP VIEW IF EXISTS hr_employee_hour_report;"""
        )
        openupgrade.logged_query(
            env.cr,
            """
UPDATE hr_employee_hour
SET project_id = aal.project_id, task_id = aal.task_id
FROM (
    SELECT id, project_id, task_id
    FROM account_analytic_line
) AS aal
WHERE aal.id = res_id AND type in ('timesheet', 'leave');""",
        )
