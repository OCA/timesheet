# Copyright 2018-2019 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    exclude_from_sale_order = fields.Boolean(
        string="Non-billable",
        related="non_allow_billable",
        readonly=False,
        help="Checking this would exclude this timesheet entry from Sale Order",
        store=True,
    )

    @api.onchange("task_id", "employee_id")
    def _onchange_task_id_employee_id(self):
        """Override implementation in sale_timesheet to call _timesheet_get_sale_line()
        instead of resolving so_line in-place"""
        if self.project_id:  # timesheet only
            self.so_line = self._timesheet_get_sale_line()
            return
        return super()._onchange_task_id_employee_id()  # pragma: no cover

    @api.onchange("exclude_from_sale_order")
    def _onchange_exclude_from_sale_order(self):
        if self.project_id:  # timesheet only
            self.so_line = self._timesheet_get_sale_line()

    @api.constrains("exclude_from_sale_order")
    def _constrains_exclude_from_sale_order(self):
        for line in self:
            if (
                line.timesheet_invoice_id
                and line.so_line.product_id.invoice_policy == "delivery"
            ):
                raise ValidationError(
                    _(
                        "You can not modify timesheets in a way that would affect "
                        "invoices since these timesheets were already invoiced."
                    )
                )

    def _timesheet_get_sale_line(self):
        self.ensure_one()
        if self.exclude_from_sale_order:
            return self.env["sale.order.line"]
        return self._timesheet_determine_sale_line(
            **self._timesheet_determine_sale_line_arguments()
        )

    @api.model
    def _timesheet_get_sale_line_dependencies(self):
        return [
            "task_id",
            "employee_id",
            "exclude_from_sale_order",
        ]

    @api.model
    def _timesheet_should_evaluate_so_line(self, values, check):
        return check(
            [
                field_name in values
                for field_name in self._timesheet_get_sale_line_dependencies()
            ]
        )

    def _timesheet_determine_sale_line_arguments(self, values=None):
        if values:
            values.get("project_id")
            return {
                "task": self.env["project.task"].sudo().browse(values.get("task_id")),
                "employee": self.env["hr.employee"]
                .sudo()
                .browse(values.get("employee_id")),
                "project": self.env["project.project"]
                .sudo()
                .browse(values.get("project_id")),
            }
        return {
            "task": self.task_id,
            "employee": self.employee_id,
            "project": self.project_id,
        }

    @api.depends(
        "exclude_from_sale_order",
        "non_allow_billable",
    )
    def _compute_timesheet_invoice_type(self):
        super(AccountAnalyticLine, self)._compute_timesheet_invoice_type()
        for line in self:
            if (
                line.project_id
                and line.task_id
                and (line.exclude_from_sale_order or line.non_allow_billable)
            ):
                line.timesheet_invoice_type = "non_billable"

    @api.model
    def _timesheet_preprocess(self, values):
        values = super()._timesheet_preprocess(values)
        if self._timesheet_should_evaluate_so_line(values, all):
            if not values.get("exclude_from_sale_order"):
                values["so_line"] = self._timesheet_determine_sale_line(
                    **self._timesheet_determine_sale_line_arguments(values)
                ).id
        return values

    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)
        if self._timesheet_should_evaluate_so_line(values, any):
            for line in self:
                result[line.id].update({"so_line": line._timesheet_get_sale_line().id})
        return result
