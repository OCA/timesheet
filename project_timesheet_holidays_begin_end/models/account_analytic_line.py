# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def _eval_date(self, vals):
        """Keep the date of an entry generated from time off.

        ``hr_timesheet_time_control`` derives the date from the start time in
        the tz of the current user. The generated entries carry the day the
        time off is booked on, and their start time is the first working hour
        of that day for the employee; seen from a user far enough away the
        same moment falls on the day before.
        """
        if (
            vals.get("date")
            and vals.get("date_time")
            and (vals.get("holiday_id") or vals.get("global_leave_id"))
        ):
            return vals
        return super()._eval_date(vals)
