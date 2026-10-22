# Copyright 2026 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged

from odoo.addons.hr_timesheet_encode_day_float.hooks import uninstall_hook


@tagged("post_install", "-at_install")
class TestTimesheetEncodeDayFloat(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.company = cls.env.company

    def test_day_uom_uses_float_factor_widget(self):
        self.assertEqual(self.uom_day.timesheet_widget, "float_factor")

    def test_uninstall_hook_restores_float_toggle(self):
        self.uom_day.timesheet_widget = "float_factor"
        uninstall_hook(self.env)
        self.assertEqual(self.uom_day.timesheet_widget, "float_toggle")

    def test_settings_days_still_uses_day_uom(self):
        settings = self.env["res.config.settings"].create(
            {"timesheet_encode_method": "days"}
        )
        settings.execute()
        self.assertEqual(self.company.timesheet_encode_uom_id, self.uom_day)

        settings = self.env["res.config.settings"].create({})
        self.assertEqual(settings.timesheet_encode_method, "days")
        self.assertTrue(settings.is_encode_uom_days)

        days_label = dict(
            self.env["res.config.settings"]._fields["timesheet_encode_method"].selection
        )["days"]
        self.assertEqual(days_label, "Days")

    def test_day_fraction_converts_to_hours(self):
        self.assertAlmostEqual(
            self.uom_day._compute_quantity(0.2, self.uom_hour, round=False),
            1.6,
            places=2,
        )
        self.assertAlmostEqual(
            self.uom_day._compute_quantity(3.0, self.uom_hour, round=False),
            24.0,
            places=2,
        )
