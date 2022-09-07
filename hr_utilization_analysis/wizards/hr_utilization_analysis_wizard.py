# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class HrUtilizationAnalysisWizard(models.TransientModel):
    _name = "hr.utilization.analysis.wizard"
    _description = "HR Utilization Analysis Wizard"

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    only_active_employees = fields.Boolean(
        string="Only Active Employees",
        default=True,
    )
    employee_ids = fields.Many2many(string="Employees", comodel_name="hr.employee")
    employee_category_ids = fields.Many2many(
        string="Employee Tags",
        comodel_name="hr.employee.category",
    )
    department_ids = fields.Many2many(
        string="Departments",
        comodel_name="hr.department",
    )

    def action_view(self):
        self.ensure_one()

        analysis = self.env["hr.utilization.analysis"].create(
            self._collect_analysis_values()
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.utilization.analysis.entry",
            "views": [[False, "graph"], [False, "pivot"]],
            "target": "main",
            "domain": [("analysis_id", "=", analysis.id)],
            "name": _("Utilization Analysis"),
        }

    def _collect_analysis_values(self):
        self.ensure_one()

        return {
            "date_from": self.date_from,
            "date_to": self.date_to,
            "only_active_employees": self.only_active_employees,
            "employee_ids": [(6, False, self.employee_ids.ids)],
            "employee_category_ids": [(6, False, self.employee_category_ids.ids)],
            "department_ids": [(6, False, self.department_ids.ids)],
        }
