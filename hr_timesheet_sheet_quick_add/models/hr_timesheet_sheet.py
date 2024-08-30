from datetime import timedelta

from odoo import api, fields, models

from .users import TASK_DAYS_HELP


class Hr_TimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    proposed_task_ids = fields.Many2many(
        comodel_name="project.task",
        readonly=False,
        store=False,
        compute="_compute_recent_tasks",
        help="Last timesheet tasks by you.\n"
        "If no time tasks is set, your tasks with no timesheet are added.",
    )
    default_hour = fields.Integer(string="Hours", default=1, help="Default hours")
    last_tasks_days = fields.Integer(
        default=lambda s: s.env.user.last_tasks_days, help=TASK_DAYS_HELP
    )
    no_time_tasks = fields.Boolean(
        help="Complete proposed tasks with no time assigned tasks"
    )

    @api.depends("timesheet_ids")
    def _compute_recent_tasks(self):
        "It get tasks on which you recorded time recently"
        for rec in self:
            recent = fields.Date.today() - timedelta(days=rec.last_tasks_days)
            # tasks with timesheet
            tasks = self.env["account.analytic.line"].read_group(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("task_id", "not in", rec.timesheet_ids.mapped("task_id").ids),
                    ("sheet_id", "!=", rec.id),
                    ("date", ">", recent),
                ],
                ["task_id", "unit_amount"],
                ["task_id"],
            )
            tasks = self.env["project.task"].browse(
                [x["task_id"] and x["task_id"][0] for x in tasks]
            )
            if rec.no_time_tasks:
                # tasks attached to employee without timesheet
                tasks |= self._get_employee_tasks_without_timesheet()
            rec.proposed_task_ids = tasks

    def write(self, vals):
        residual_tasks = "proposed_task_ids" in vals and vals["proposed_task_ids"][0][2]
        for rec in self:
            if "proposed_task_ids" in vals:
                rec._add_timesheet_from_proposed(residual_tasks)
        vals["name"] = "/"
        return super().write(vals)

    def _add_timesheet_from_proposed(self, residual_tasks):
        self.ensure_one()
        residual_tasks = residual_tasks or []
        task_ids = [x for x in self.proposed_task_ids.ids if x not in residual_tasks]
        values = self._prepare_empty_analytic_line()
        for task in self.env["project.task"].browse(task_ids):
            tvals = values.copy()
            tvals.update(
                {
                    "project_id": task.project_id.id,
                    "task_id": task.id,
                    "unit_amount": self.default_hour,
                    "name": "/",
                }
            )
            date = fields.Date.today()
            if date >= self.date_start and date <= self.date_end:
                tvals["date"] = date
            self.timesheet_ids |= self.env["account.analytic.line"]._sheet_create(tvals)

    def _get_employee_tasks_without_timesheet(self):
        tasks = self.env["project.task"].search(self._get_domain_wo_timesheet())
        user = self.employee_id.user_id
        return tasks.filtered(lambda s: not s.timesheet_ids.employee_id.user_id == user)

    def _get_domain_wo_timesheet(self):
        "You may inherit to customize your conditions"
        return [
            ("is_closed", "=", False),
            ("user_ids", "in", self.employee_id.user_id.id),
        ]
