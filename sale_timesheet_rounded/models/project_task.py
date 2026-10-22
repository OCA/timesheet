# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    effective_hours_rounded = fields.Float(
        string="Rounded Time Spent",
        compute="_compute_effective_hours_rounded",
        compute_sudo=True,
        store=True,
    )
    subtask_effective_hours_rounded = fields.Float(
        string="Rounded Subtasks Time Spent",
        compute="_compute_subtask_effective_hours_rounded",
        recursive=True,
        store=True,
    )
    remaining_hours_rounded = fields.Float(
        string="Rounded Time Remaining",
        compute="_compute_remaining_hours_rounded",
        compute_sudo=True,
        store=True,
    )
    total_hours_spent_rounded = fields.Float(
        string="Rounded Total Time Spent",
        compute="_compute_total_hours_spent_rounded",
        store=True,
    )

    @api.depends("timesheet_ids.unit_amount_rounded")
    def _compute_effective_hours_rounded(self):
        timesheet_rg = self.env["account.analytic.line"]._read_group(
            [("task_id", "in", self.ids)],
            ["task_id"],
            ["unit_amount_rounded:sum"],
        )
        per_task = {task.id: amount for task, amount in timesheet_rg}
        for task in self:
            task.effective_hours_rounded = per_task.get(task.id, 0.0)

    @api.depends(
        "child_ids.effective_hours_rounded", "child_ids.subtask_effective_hours_rounded"
    )
    def _compute_subtask_effective_hours_rounded(self):
        for task in self.with_context(active_test=False):
            task.subtask_effective_hours_rounded = sum(
                child_task.effective_hours_rounded
                + child_task.subtask_effective_hours_rounded
                for child_task in task.child_ids
            )

    @api.depends(
        "effective_hours_rounded", "subtask_effective_hours_rounded", "allocated_hours"
    )
    def _compute_remaining_hours_rounded(self):
        for task in self:
            if not task.allocated_hours:
                task.remaining_hours_rounded = 0.0
            else:
                task.remaining_hours_rounded = (
                    task.allocated_hours
                    - task.effective_hours_rounded
                    - task.subtask_effective_hours_rounded
                )

    @api.depends("effective_hours_rounded", "subtask_effective_hours_rounded")
    def _compute_total_hours_spent_rounded(self):
        for task in self:
            task.total_hours_spent_rounded = (
                task.effective_hours_rounded + task.subtask_effective_hours_rounded
            )
