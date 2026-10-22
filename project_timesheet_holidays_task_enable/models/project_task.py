# © 2025 Solvos Consultoría Informática (<https://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    timeoff_enable_use_timesheets = fields.Boolean(
        string="Enable use in timesheets when Used in Time Off",
        help="""
        For a time off task, re-enables it usage in timesheets
        """,
    )

    def _compute_is_timeoff_task(self):
        res = super()._compute_is_timeoff_task()
        self.filtered(
            lambda x: x.is_timeoff_task and x.timeoff_enable_use_timesheets
        ).is_timeoff_task = False
        return res

    def _search_is_timeoff_task(self, operator, value):
        domain = super()._search_is_timeoff_task(operator, value)
        domain_list = list(domain[0])

        tasks_ids = domain_list[2]
        new_tasks = self.browse(tasks_ids).filtered(
            lambda x: x.timeoff_enable_use_timesheets
            if value
            else not x.timeoff_enable_use_timesheets
        )
        domain_list[2] = new_tasks.ids
        return [tuple(domain_list)]
