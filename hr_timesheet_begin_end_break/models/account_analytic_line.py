# Copyright 2025 Slivi-sliv
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import timedelta

from odoo import api, exceptions, fields, models
from odoo.tools.float_utils import float_compare


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    break_duration = fields.Float(default=0.0)

    @api.onchange("time_start", "time_stop", "break_duration")
    def onchange_hours_start_stop(self):
        res = super().onchange_hours_start_stop()
        if self.time_start and self.time_stop:
            # Re-compute the worked amount so that the break is deducted.
            start = timedelta(hours=self.time_start)
            stop = timedelta(hours=self.time_stop)
            if stop >= start:
                self.unit_amount = (stop - start).seconds / 3600 - self.break_duration
        return res

    @api.constrains("time_start", "time_stop", "unit_amount", "break_duration")
    def _check_time_start_stop(self):
        # This overrides (does not extend) the base ``hr_timesheet_begin_end``
        # constraint of the same name: the base enforces
        # ``unit_amount == time_stop - time_start``, which is always false once a
        # break is deducted. We therefore re-check start/stop order and overlap
        # here as well, mirroring the base implementation, and add
        # ``break_duration`` to the duration expectation.
        rounding = self.env.ref("uom.product_uom_hour").rounding
        value_to_html = self.env["ir.qweb.field.float_time"].value_to_html
        for line in self:
            if not line.time_start and not line.time_stop:
                continue
            start = timedelta(hours=line.time_start)
            stop = timedelta(hours=line.time_stop)
            if stop < start:
                raise exceptions.ValidationError(
                    self.env._(
                        "The beginning hour (%(html_start)s) must "
                        "precede the ending hour (%(html_stop)s).",
                        html_start=value_to_html(line.time_start, None),
                        html_stop=value_to_html(line.time_stop, None),
                    )
                )
            hours = (stop - start).seconds / 3600 - line.break_duration
            if hours and float_compare(
                hours, line.unit_amount, precision_rounding=rounding
            ):
                raise exceptions.ValidationError(
                    self.env._(
                        "The duration (%(html_unit_amount)s) must be equal to the "
                        "difference between the hours minus the break "
                        "(%(html_hours)s).",
                        html_unit_amount=value_to_html(line.unit_amount, None),
                        html_hours=value_to_html(hours, None),
                    )
                )
            # check if lines overlap
            others = self.search(
                [
                    ("id", "!=", line.id),
                    ("employee_id", "=", line.employee_id.id),
                    ("date", "=", line.date),
                    ("time_start", "<", line.time_stop),
                    ("time_stop", ">", line.time_start),
                ]
            )
            if others:
                lines_str = "\n".join(
                    [
                        f"{value_to_html(other.time_start, None)} - "
                        f"{value_to_html(other.time_stop, None)}"
                        for other in (line + others).sorted(
                            key=lambda item: item.time_start
                        )
                    ]
                )
                raise exceptions.ValidationError(
                    self.env._("Lines can't overlap:\n%s") % (lines_str,)
                )
