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
            "project_id" in field_list
            and not self.env.context.get("default_project_id")
            and self.env.context.get("is_timesheet")
            and result.get("project_id", False)
        ):
            # The default project without the autofill from previous entries
            default_project_id = (
                self.with_context(is_timesheet=False)
                .default_get(["project_id"])
                .get("project_id", False)
            )
            if result["project_id"] != default_project_id:
                _logger.debug(
                    "Favourite project %s not autofilled", result["project_id"]
                )
                result["project_id"] = default_project_id
        return result
