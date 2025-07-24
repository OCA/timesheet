# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SheetWarningItem(models.Model):
    _name = "hr_timesheet.sheet.warning.item"
    _description = "Timesheet Sheet Warning Item"
    _order = "id desc"

    warning_definition_id = fields.Many2one(
        comodel_name="hr_timesheet.sheet.warning.definition",
    )
    sheet_id = fields.Many2one(comodel_name="hr_timesheet.sheet", ondelete="cascade")
    name = fields.Char(
        compute="_compute_name",
    )
    company_id = fields.Many2one(
        related="sheet_id.company_id",
        store=True,
    )

    _sql_constraints = [
        (
            "unique_warning",
            "unique(sheet_id, warning_definition_id)",
            "Timesheet warning has to be unique for timesheet sheet.",
        )
    ]

    def _compute_name(self):
        for rec in self:
            rec.name = (
                f"{rec.warning_definition_id.display_name} "
                f"in {rec.sheet_id.complete_name}"
            )
