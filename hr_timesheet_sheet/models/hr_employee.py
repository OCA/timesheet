# Copyright 2018 ForgeFlow, S.L.
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    timesheet_sheet_count = fields.Integer(
        compute="_compute_timesheet_sheet_count", string="Timesheet Sheets Count"
    )

    def _compute_timesheet_sheet_count(self):
        Sheet = self.env["hr_timesheet.sheet"]
        for employee in self:
            employee.timesheet_sheet_count = Sheet.search_count(
                [("employee_id", "=", employee.id)]
            )

    @api.constrains("company_id")
    def _check_company_id(self):
        for rec in self.sudo().filtered("company_id"):
            for field in [
                rec.env["hr_timesheet.sheet"].search(
                    [
                        ("employee_id", "=", rec.id),
                        ("company_id", "!=", rec.company_id.id),
                        ("company_id", "!=", False),
                    ],
                    limit=1,
                )
            ]:
                if (
                    rec.company_id
                    and field.company_id
                    and rec.company_id != field.company_id
                ):
                    raise ValidationError(
                        _(
                            "You cannot change the company, "
                            "as this %(rec_name)s (%(rec_display_name)s) "
                            "is assigned to %(current_name)s (%(current_display_name)s).",
                            rec_name=rec._name,
                            rec_display_name=rec.display_name,
                            current_name=field._name,
                            current_display_name=field.display_name,
                        )
                    )
