from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env["ir.ui.view"].search(
        [("key", "=", "hr_timesheet.portal_my_home_timesheet"), ("active", "=", False)]
    )
    if view:
        view.active = True
        _logger.info(
            "Re-activated 'hr_timesheet.portal_my_home_timesheet' view during module uninstall."
        )
