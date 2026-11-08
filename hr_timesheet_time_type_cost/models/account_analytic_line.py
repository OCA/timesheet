# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .project_time_type import COST_TYPE_SELECTION

# Values copied from the time type when the line is created or its time type
# changes. They are derived data: a caller must not set them directly.
SNAPSHOT_FIELDS = (
    "time_type_cost_type",
    "time_type_cost_ratio",
    "time_type_fixed_cost",
)
# Same groups as the fixed cost of the time type.
FIXED_COST_GROUPS = "project.group_project_manager,hr.group_hr_user"


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

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
        currency_field="currency_id",
        readonly=True,
        copy=False,
        groups=FIXED_COST_GROUPS,
        help="Fixed hourly cost applied when the line was created, in the "
        "company currency. The rate is positive; the analytic amount carries "
        "the sign.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = []
        for vals in vals_list:
            vals = dict(vals)
            # The snapshot is derived from the time type, so it is always
            # overwritten: a caller cannot inject a cost rate.
            vals.update(self._time_type_cost_snapshot(vals.get("time_type_id")))
            prepared_vals_list.append(vals)
        return super().create(prepared_vals_list)

    def write(self, values):
        values = dict(values)
        if "time_type_id" not in values:
            # The snapshot is derived data: drop direct writes to it.
            values = {k: v for k, v in values.items() if k not in SNAPSHOT_FIELDS}
            return super().write(values) if values else True
        # Only lines whose time type really changes take the current rule of
        # the time type and are repriced. Writing the same time type again
        # (mass edit, import, API) must not reprice historic lines.
        time_type_id = values["time_type_id"] or False
        unchanged = self.filtered(lambda line: line.time_type_id.id == time_type_id)
        changed = self - unchanged
        result = True
        other_values = {
            key: value
            for key, value in values.items()
            if key != "time_type_id" and key not in SNAPSHOT_FIELDS
        }
        if unchanged and other_values:
            result = super(AccountAnalyticLine, unchanged).write(other_values)
        if changed:
            snapshot = self._time_type_cost_snapshot(time_type_id)
            # The fixed cost of the time type is restricted to HR and project
            # managers. The line still has to carry it for every user, so it
            # is written first with sudo; the user write below then triggers
            # the amount recompute with the snapshotted value.
            if not self.env.su and not self.env.user.has_groups(FIXED_COST_GROUPS):
                # Bypass this write() so the guard below does not drop the
                # snapshot value; the user write then triggers the recompute.
                super(AccountAnalyticLine, changed.sudo()).write(
                    {"time_type_fixed_cost": snapshot.pop("time_type_fixed_cost")}
                )
            values.update(snapshot)
            result = super(AccountAnalyticLine, changed).write(values) and result
        return result

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
