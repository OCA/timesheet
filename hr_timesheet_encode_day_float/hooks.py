# Copyright 2026 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    """Restore the standard day timesheet widget on module uninstall."""
    uom_day = env.ref("uom.product_uom_day", raise_if_not_found=False)
    if uom_day and uom_day.timesheet_widget != "float_toggle":
        uom_day.timesheet_widget = "float_toggle"
