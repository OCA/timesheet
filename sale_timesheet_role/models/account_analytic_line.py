# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.onchange("role_id")
    def _onchange_role_id(self):
        if self.project_id:  # timesheet only
            self.so_line = self._timesheet_get_sale_line()

    @api.constrains("role_id")
    def _check_role_id(self):
        super()._check_role_id()
        if self.filtered(
            lambda line: line.timesheet_invoice_id and
                line.so_line.product_id.invoice_policy == "delivery"
        ):
            raise ValidationError(_(
                "You can not modify timesheets in a way that would affect"
                " invoices since these timesheets were already invoiced."
            ))

    @api.multi
    def _get_valid_so_line_ids(self):
        self.ensure_one()
        return (
            super()._get_valid_so_line_ids()
            | self.project_id.mapped(
                "sale_line_employee_role_ids.sale_line_id"
            )
        )

    @api.multi
    def _timesheet_determine_sale_line_arguments(self, values=None):
        res = super()._timesheet_determine_sale_line_arguments(values)
        res.update({
            "role": (
                self.env["project.role"].sudo().browse(values["role_id"])
            ) if values and "role_id" in values else self.role_id,
        })
        return res

    @api.model
    def _timesheet_get_sale_line_dependencies(self):
        res = super()._timesheet_get_sale_line_dependencies()
        res.append("role_id")
        return res

    @api.model
    def _timesheet_determine_sale_line(self, task, employee, role=None,
                                       **kwargs):
        if task.billable_type != "employee_role_rate":
            return super()._timesheet_determine_sale_line(
                task,
                employee,
                **kwargs
            )

        Map = self.env["project.employee.role.sale.order.line.map"]

        mapping = Map.search([
            ("project_id", "=", task.project_id.id),
            ("employee_id", "=", employee.id),
            ("role_id", "=", role.id),
        ])
        if not mapping:
            mapping = Map.search([
                ("project_id", "=", task.project_id.id),
                ("employee_id", "=", employee.id),
                ("role_id", "=", False),
            ])
        if not mapping:
            mapping = Map.search([
                ("project_id", "=", task.project_id.id),
                ("employee_id", "=", False),
                ("role_id", "=", role.id),
            ])
        if not mapping:
            return self.env["sale.order.line"]
        return mapping.sale_line_id
