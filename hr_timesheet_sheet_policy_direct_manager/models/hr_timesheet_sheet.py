# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    @api.depends("employee_id.parent_id.user_id")
    def _compute_direct_manager_as_reviewer(self):
        self._compute_possible_reviewer_ids()

    def _get_possible_reviewers(self):
        self.ensure_one()
        res = super()._get_possible_reviewers()
        if self.review_policy == "direct_manager":
            employee = self.sudo().employee_id
            if employee.parent_id:
                res |= employee.parent_id.user_id
            elif employee.child_ids:
                # A top Manager can approve his own timesheet sheets
                res |= employee.user_id
        return res

    def _check_can_review(self):
        res = super()._check_can_review()
        if self.filtered(
            lambda x: not x.can_review and x.review_policy == "direct_manager"
        ):
            raise UserError(_("Only a employee's Direct Manager can review the sheet."))
        return res
