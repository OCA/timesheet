# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    billable_type = fields.Selection(
        selection_add=[
            ("employee_role_rate", "At Employee/Role Rate")
        ],
    )
    sale_line_employee_role_ids = fields.One2many(
        string="Employee/Role <> Sale Order Line mapping",
        comodel_name="project.employee.role.sale.order.line.map",
        inverse_name="project_id",
        copy=False,
    )

    @api.multi
    @api.depends("sale_line_employee_role_ids")
    def _compute_billable_type(self):
        result = super()._compute_billable_type()
        for project in self:
            if project.sale_line_employee_role_ids:
                project.billable_type = "employee_role_rate"
        return result
