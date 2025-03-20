# Copyright 2025 Innovara Ltd - Manuel Fombuena
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if (
            not self._context.get("default_project_id")
            and self._context.get("is_timesheet")
            and result.get("project_id", False)
        ):
            result["project_id"] = False
            _logger.debug("project_id set to False")
        return result
