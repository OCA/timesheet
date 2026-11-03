# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .project_time_type import COST_TYPE_SELECTION


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    time_type_id = fields.Many2one(
        comodel_name="project.time.type",
        string="Time Type",
        check_company=True,
    )
    time_type_cost_type = fields.Selection(
        selection=COST_TYPE_SELECTION,
        readonly=True,
        copy=False,
        help="Cost rule of the time type when the line was created.",
    )
    time_type_cost_ratio = fields.Float(
        readonly=True,
        copy=False,
        help="Ratio over the employee cost applied when the line was created.",
    )
    time_type_fixed_cost = fields.Monetary(
        currency_field="company_currency_id",
        readonly=True,
        copy=False,
        help="Fixed hourly cost applied when the line was created, in the "
        "company currency. The rate is positive; the analytic amount carries "
        "the sign.",
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Company Currency",
        related="company_id.currency_id",
        readonly=True,
        help="Currency of the line company, used by the fixed cost snapshot.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = []
        for vals in vals_list:
            vals = dict(vals)
            if vals.get("time_type_id"):
                for key, value in self._time_type_cost_snapshot(
                    vals["time_type_id"]
                ).items():
                    vals.setdefault(key, value)
            prepared_vals_list.append(vals)
        return super().create(prepared_vals_list)

    def write(self, values):
        if "time_type_id" in values:
            values = dict(values)
            for key, value in self._time_type_cost_snapshot(
                values["time_type_id"]
            ).items():
                values.setdefault(key, value)
        return super().write(values)

    def _timesheet_postprocess_values(self, values):
        # Core only recomputes the amount when one of its own cost inputs
        # changes. A new time type changes the cost too, so a core trigger key
        # is added to the values; core still reads the real values from the
        # records and keeps owning the amount formula.
        if "time_type_id" in values:
            values = dict(values)
            values.setdefault("unit_amount", 0.0)
        return super()._timesheet_postprocess_values(values)

    def _hourly_cost(self):
        self.ensure_one()
        return self._apply_time_type_cost(super()._hourly_cost())

    def _apply_time_type_cost(self, cost):
        """Return the hourly cost of the line for a resolved base cost.

        ``cost`` is the hourly cost resolved by the other installed modules: the
        employee cost, or the mapped cost of an employee-rate project when
        ``sale_timesheet`` is installed. It is positive, like the employee
        hourly cost, because core applies the sign when it computes the
        analytic amount.
        """
        if self.time_type_cost_type == "fixed":
            cost = self.time_type_fixed_cost
            if not self.employee_id:
                return cost
            company = self.company_id or self.env.company
            return company.currency_id._convert(
                cost,
                self.employee_id.currency_id,
                company,
                self.date,
            )
        if self.time_type_cost_type == "ratio":
            cost *= self.time_type_cost_ratio
        return cost

    @api.model
    def _time_type_cost_snapshot(self, time_type_id):
        """Return the cost values the given time type imposes on a line."""
        if not time_type_id:
            return {
                "time_type_cost_type": False,
                "time_type_cost_ratio": 0.0,
                "time_type_fixed_cost": 0.0,
            }
        time_type = self.env["project.time.type"].sudo().browse(time_type_id)
        return {
            "time_type_cost_type": time_type.cost_type,
            "time_type_cost_ratio": time_type.cost_ratio,
            "time_type_fixed_cost": time_type.fixed_cost,
        }
