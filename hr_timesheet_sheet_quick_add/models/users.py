from odoo import _, fields, models

TASK_DAYS_HELP = _(
    "Horizon from which we search for the tasks on which we have entered timesheets"
)


class ResUsers(models.Model):
    _inherit = "res.users"

    last_tasks_days = fields.Integer(default=14, help=TASK_DAYS_HELP)
