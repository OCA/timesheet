# Copyright 2022 Dinar Gabbasov
# Copyright 2022 Ooops404
# Copyright 2022 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.constrains("date")
    def _check_project_date(self):
        """
        Check that the date can be changed for the project.
        """
        if self.user_has_groups(
            "hr_timesheet_time_restriction.group_timesheet_time_manager"
        ):
            return True

        timesheet_restriction_days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "hr_timesheet_time_restriction.timesheet_restriction_days",
                0,
            )
        )
        today = date.today()
        for record in self.filtered(lambda rec: rec.date and rec.project_id):
            days = (
                record.project_id.timesheet_restriction_days
                or timesheet_restriction_days
            )
            if days and today - relativedelta(days=days) > record.date:
                raise ValidationError(
                    _(
                        "You cannot change or create a timesheet "
                        'with a specified "date" in the past.'
                    ),
                )
