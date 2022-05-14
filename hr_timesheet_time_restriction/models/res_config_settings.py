from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.onchange("timesheet_restriction_days")
    def _onchange_timesheet_restriction_days(self):
        """
        Check that `timesheet_restriction_days` not negative
        """
        if self.timesheet_restriction_days < 0:
            self.timesheet_restriction_days = 0
            return {
                "warning": {
                    "title": _("Warning!"),
                    "message": _(
                        "The day of the timesheet restriction must not be negative."
                    ),
                },
            }

    timesheet_restriction_days = fields.Integer(
        config_parameter="hr_timesheet_time_restriction.timesheet_restriction_days",
        default=0,
    )
