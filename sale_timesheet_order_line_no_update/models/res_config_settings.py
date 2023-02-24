from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_hide_original_sol = fields.Boolean(
        "Hide Sale Order Item in Task",
        config_parameter="sale_timesheet_order_line_no_update.default_hide_original_sol",
        default_model="project.task",
        default=True,
    )
