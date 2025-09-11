# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)

from contextlib import suppress

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_preprocess_get_accounts(self, vals):
        # Synchronisation of analytic accounts from task to propagate them to timesheets
        project_analytic_accounts = super()._timesheet_preprocess_get_accounts(vals)
        if self.env.context.get(
            "project_task_analytic_propagation"
        ):  # When call project.task._recalculate_timesheet_analytic_accounts
            return project_analytic_accounts
        task = self.env["project.task"].sudo().browse(vals.get("task_id"))
        if not task:
            return project_analytic_accounts
        with suppress(KeyError):
            task_analytic_accounts = {
                fname: task[fname].id for fname in self._get_plan_fnames()
            }
            project_analytic_accounts.update(task_analytic_accounts)
        return project_analytic_accounts

    @api.depends("task_id.project_id")
    def _compute_project_id(self):
        self = self.with_context(propagate_project_id=True)
        return super()._compute_project_id()

    def _is_not_billed(self):
        if not self.env.context.get("propagate_project_id"):
            return super()._is_not_billed()
        return True

    def write(self, values):
        self = self.with_context(propagate_project_id_for_timesheet=True)
        return super().write(values)

    def _check_can_write(self, values):
        # Allow propagate project_id from task to all
        # timesheets (invoiced and not invoiced)
        if (
            self.env.context.get("propagate_project_id_for_timesheet")
            and "project_id" in values
        ):
            return
        return super()._check_can_write(values)
