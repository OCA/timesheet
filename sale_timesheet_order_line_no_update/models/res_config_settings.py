# Copyright 2023 ooops404 - Ilyas
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_hide_original_sol = fields.Boolean(
        "Hide Sale Order Item in Task",
        config_parameter=(
            "sale_timesheet_order_line_no_update.default_hide_original_sol"
        ),
        default_model="project.task",
        default=False,
    )

    default_select_all_project_sale_items = fields.Boolean(
        "Select items from different SO in project",
        config_parameter=(
            "sale_timesheet_order_line_no_update.default_select_all_project_sale_items"
        ),
        default_model="project.project",
        default=False,
    )
