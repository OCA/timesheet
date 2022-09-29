# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model_create_multi
    def create(self, vals_list):
        employee_model = self.env["hr.employee"]
        for vals in vals_list:
            if vals.get("employee_id") and vals.get("project_id"):
                employee = employee_model.browse(vals.get("employee_id")).sudo()
                if employee.timesheet_analytic_tag_ids:
                    vals["tag_ids"] = vals.get("tag_ids", [])
                    vals["tag_ids"] += [
                        (4, tag.id) for tag in employee.timesheet_analytic_tag_ids
                    ]
        return super().create(vals_list)
