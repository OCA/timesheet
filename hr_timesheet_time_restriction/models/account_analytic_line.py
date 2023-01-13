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
        use_timesheet_restriction = (
            True
            if self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_timesheet_time_restriction.use_timesheet_restriction", False)
            else False
        )

        for record in self.filtered(lambda rec: rec.date and rec.project_id):
            if use_timesheet_restriction or record.project_id.use_timesheet_restriction:
                days = (
                    record.project_id.timesheet_restriction_days
                    or timesheet_restriction_days
                )
                if days and today - relativedelta(days=days) > record.date:
                    raise ValidationError(
                        _(
                            "You cannot set a timesheet more than"
                            " {days} days from current date.".format(
                                days=record.project_id.timesheet_restriction_days
                            ),
                        )
                    )
                if (
                    record.project_id.timesheet_restriction_days
                    == timesheet_restriction_days
                    == 0
                    and today != record.date
                ):
                    raise ValidationError(
                        _(
                            "You cannot set a timesheet for a "
                            "date different from current date"
                        )
                    )
