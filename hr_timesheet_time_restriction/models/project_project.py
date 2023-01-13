# Copyright 2022 Dinar Gabbasov
# Copyright 2022 Ooops404
# Copyright 2022 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.constrains("timesheet_restriction_days")
    def _check_timesheet_restriction_days(self):
        """
        Check that the `timesheet_restriction_days` is positive
        """
        use_timesheet_restriction = (
            True
            if self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_timesheet_time_restriction.use_timesheet_restriction", False)
            else False
        )
        for record in self:
            if use_timesheet_restriction:
                if record.timesheet_restriction_days < 0:
                    raise ValidationError(
                        _("The day of the timesheet restriction must not be negative.")
                    )

    timesheet_restriction_days = fields.Integer(
        default=0, help="Not active if equal to 0."
    )

    use_timesheet_restriction = fields.Boolean(
        default=lambda self: True
        if self.env["ir.config_parameter"]
        .sudo()
        .get_param("hr_timesheet_time_restriction.use_timesheet_restriction", False)
        else False
    )
