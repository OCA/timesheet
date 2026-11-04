from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetReportWizardExtra(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["hr.timesheet.report.wizard"]

    def _entry_field_cmd(self):
        return [
            Command.create(
                {
                    "sequence": 10,
                    "field_name": "name",
                    "field_title": "Name",
                    "field_type": "char",
                }
            )
        ]

    @mute_logger("odoo.models.unlink")
    def test_create_sets_empty_grouping_if_missing(self):
        wizard = self.Wizard.create(
            {
                "entry_field_ids": self._entry_field_cmd(),
            }
        )
        self.assertFalse(wizard.grouping_field_ids)
        self.assertEqual(len(wizard.entry_field_ids), 1)

    @mute_logger("odoo.models.unlink")
    def test_create_without_entry_fields_raises_usererror(self):
        with self.assertRaises(UserError):
            self.Wizard.create({})

    @mute_logger("odoo.models.unlink")
    def test_constrains_entry_field_ids_empty_raises_validationerror(self):
        with self.assertRaises(ValidationError):
            self.Wizard.create(
                {
                    "grouping_field_ids": [Command.clear()],
                    "entry_field_ids": [
                        Command.clear()
                    ],  # key exists, but empty => constraint
                }
            )

    @mute_logger("odoo.models.unlink")
    def test_action_export_html_target_main_when_no_lines(self):
        wizard = self.Wizard.create(
            {
                "grouping_field_ids": [Command.clear()],
                "entry_field_ids": [
                    Command.create(
                        {
                            "sequence": 10,
                            "field_name": "name",
                            "field_title": "Name",
                            "field_type": "char",
                        }
                    )
                ],
            }
        )
        action = wizard.action_export_html()
        self.assertEqual(action.get("target"), "main")

    @mute_logger("odoo.models.unlink")
    def test_action_export_xlsx_calls_generate_report(self):
        wizard = self.Wizard.create(
            {
                "grouping_field_ids": [Command.clear()],
                "entry_field_ids": self._entry_field_cmd(),
            }
        )
        action = wizard.action_export_xlsx()
        self.assertIsInstance(action, dict)
