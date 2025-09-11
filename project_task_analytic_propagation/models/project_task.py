# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)
from contextlib import suppress

from odoo import api, fields, models


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "analytic.plan.fields.mixin"]

    account_id = fields.Many2one(
        compute="_compute_task_analytic_accounts",
        readonly=False,
        store=True,
    )

    def _get_project_analytic_plan_columns(self):
        return [
            f"project_id.{x}"
            for x in self.project_id._get_plan_fnames()
            if self._fields.get(x)
        ]

    @api.depends(lambda self: self._get_project_analytic_plan_columns())
    def _compute_task_analytic_accounts(self):
        plan_fnames = self._get_plan_fnames()
        for task in self._origin:
            # By using _origin, new records (with a NewId) are excluded and
            # the computation works automagically for virtual onchange records as well
            task_analytic_accounts = {}
            with suppress(KeyError):
                for fname in plan_fnames:
                    task[fname] = task.project_id[fname]
                    task_analytic_accounts.update({fname: task[fname].id})
            if task_analytic_accounts:
                task._recalculate_timesheet_analytic_accounts(task_analytic_accounts)

    def _recalculate_timesheet_analytic_accounts(self, analytic_accounts):
        fnames = list(analytic_accounts.keys())
        # If the analytic accounts are not equal between the task and the timesheet
        timesheets = self.timesheet_ids.filtered(
            lambda line: {fname: line[fname].id for fname in fnames}
            != analytic_accounts
        )
        if timesheets:
            timesheets.with_context(project_task_analytic_propagation=True).write(
                analytic_accounts
            )

    def write(self, vals):
        res = super().write(vals)
        vals_analytic_accounts = {
            key: value for key, value in vals.items() if key in self._get_plan_fnames()
        }
        if "timesheet_ids" in vals and not vals_analytic_accounts:
            # By default, the timesheet line takes the analytic accounts values
            # from the project, but we need to recalculate them when we create
            # a timesheet line
            for task in self:
                task._recalculate_timesheet_analytic_accounts(
                    {fname: task[fname].id for fname in self._get_plan_fnames()}
                )
        if vals_analytic_accounts:
            self._recalculate_timesheet_analytic_accounts(vals_analytic_accounts)
        return res

    @api.constrains(lambda self: self._get_plan_fnames())
    def _check_account_id(self):
        # Overriden from 'analytic.plan.fields.mixin'
        pass
