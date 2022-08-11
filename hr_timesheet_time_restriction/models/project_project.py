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
        for record in self:
            if record.timesheet_restriction_days < 0:
                raise ValidationError(
                    _("The day of the timesheet restriction must not be negative.")
                )

    timesheet_restriction_days = fields.Integer(
        default=0, help="Not active if equal to 0."
    )
