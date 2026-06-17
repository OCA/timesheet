# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain


class HrDepartment(models.Model):
    _inherit = "hr.department"

    timesheet_sheet_to_approve_count = fields.Integer(
        compute="_compute_timesheet_to_approve", string="Timesheet Sheets to Approve"
    )

    def _compute_timesheet_to_approve(self):
        timesheet_data = self.env["hr_timesheet.sheet"]._read_group(
            domain=Domain.AND(
                [
                    Domain("department_id", "in", self.ids),
                    Domain("state", "=", "confirm"),
                ]
            ),
            groupby=["department_id"],
            aggregates=["department_id:count"],
        )
        # timesheet data contains a list of (department_id: count_for_department_id)
        result = {data[0].id: data[1] for data in timesheet_data}
        for department in self:
            department.timesheet_sheet_to_approve_count = result.get(department.id, 0)

    @api.constrains("company_id")
    def _check_company_id(self):
        for rec in self.sudo().filtered("company_id"):
            for field in [
                rec.env["hr_timesheet.sheet"].search(
                    Domain.AND(
                        [
                            Domain("department_id", "=", rec.id),
                            Domain("company_id", "!=", rec.company_id.id),
                            Domain("company_id", "!=", False),
                        ]
                    ),
                    limit=1,
                )
            ]:
                if (
                    rec.company_id
                    and field.company_id
                    and rec.company_id != field.company_id
                ):
                    raise ValidationError(
                        rec.env._(
                            "You cannot change the company, as this"
                            " %(rec_name)s (%(rec_display_name)s) is assigned"
                            " to %(current_name)s (%(current_display_name)s).",
                            rec_name=rec._name,
                            rec_display_name=rec.display_name,
                            current_name=field._name,
                            current_display_name=field.display_name,
                        )
                    )
