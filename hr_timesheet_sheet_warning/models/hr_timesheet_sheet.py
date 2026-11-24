# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Sheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    hr_timesheet_sheet_warning_item_ids = fields.One2many(
        comodel_name="hr_timesheet.sheet.warning.item",
        inverse_name="sheet_id",
        readonly=True,
    )

    def _generate_hr_timesheet_sheet_warnings(self):
        definitions = self.env["hr_timesheet.sheet.warning.definition"].search(
            [("active", "in", [True, False])]
        )
        item_model = self.env["hr_timesheet.sheet.warning.item"]

        for rec in self:
            for definition in definitions:
                existing = item_model.search(
                    [
                        ("sheet_id", "=", rec.id),
                        ("warning_definition_id", "=", definition.id),
                    ]
                )
                warning_applicable = definition.is_warning_applicable(rec)
                if warning_applicable:
                    warning_raised = definition.evaluate_definition(rec)
                    if not definition.active:
                        warning_raised = False

                    if warning_raised and not existing:
                        item_model.create(
                            {"sheet_id": rec.id, "warning_definition_id": definition.id}
                        )
                    elif not warning_raised and existing:
                        existing.unlink()
                elif not warning_applicable and existing:
                    existing.unlink()

    def action_generate_warnings(self):
        self._generate_hr_timesheet_sheet_warnings()
        return True

    def action_timesheet_confirm(self):
        self.action_generate_warnings()
        return super().action_timesheet_confirm()
