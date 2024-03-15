# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SheetGeneratedAttendancesSelection(models.TransientModel):
    _name = "hr_timesheet.sheet.generated.attendances.selection"
    _description = "Timesheet Sheet Generated Attendances Selection"

    original_attendance_ids = fields.Many2many(
        comodel_name="hr.attendance",
        relation="timesheet_sheet_originally_generated_attendances",
        string="Originally Generated Attendances",
    )
    attendance_ids = fields.Many2many(
        comodel_name="hr.attendance",
        relation="timesheet_sheet_generated_attendances",
        string="Generated Attendances",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(SheetGeneratedAttendancesSelection, self).default_get(fields_list)
        attendances_to_add = [
            (4, attendance_id) for attendance_id in self.env.context["attendances"]
        ]
        res["original_attendance_ids"] = attendances_to_add
        res["attendance_ids"] = attendances_to_add
        return res

    def action_save(self):
        # Only delete the records that have been removed
        # from the wizard by the user
        attendances_for_deletion = self.original_attendance_ids - self.attendance_ids
        attendances_for_deletion.sudo().unlink()
