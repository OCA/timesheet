# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["account.analytic.plan"].search([])._sync_plan_column("project.task")
    default_analytic_plan = int(
        env["ir.config_parameter"].sudo().get_param("analytic.project_plan", 0)
    )
    env.cr.execute("""
        SELECT pt.id, pt.account_id, ac.plan_id
            FROM project_task AS pt
        INNER JOIN account_analytic_account as ac ON (ac.id=pt.account_id)
            WHERE pt.account_id IS NOT NULL
        """)
    rows = env.cr.fetchall()
    for task_id, analytic_account_id, plan_id in rows:
        column_name = (
            f"x_plan{plan_id}_id" if plan_id != default_analytic_plan else "account_id"
        )
        if column_name != "account_id":
            query = f"""
                UPDATE project_task
                SET {column_name} = %s,
                    account_id = project_project.account_id
                FROM project_project
                WHERE project_task.id = %s
                AND project_project.id = project_task.project_id
            """
            env.cr.execute(query, (analytic_account_id, task_id))

    all_task_with_timesheets = env["project.task"].search(
        [("timesheet_ids", "!=", False)]
    )
    for task in all_task_with_timesheets:
        vals_analytic_accounts = {
            fname: task[fname].id for fname in task._get_plan_fnames()
        }
        task._recalculate_timesheet_analytic_accounts(vals_analytic_accounts)
