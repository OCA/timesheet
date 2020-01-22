# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.multi
    @api.depends('employee_id.parent_id.user_id')
    def _compute_direct_manager_as_reviewer(self):
        self._compute_possible_reviewer_ids()

    @api.multi
    def _get_possible_reviewers(self):
        self.ensure_one()
        res = super()._get_possible_reviewers()
        if self.review_policy == 'direct_manager':
            if self.employee_id.parent_id:
                res |= self.employee_id.parent_id.user_id
            elif self.employee_id.child_ids:
                # A top Manager can approve his own timesheet sheets
                res |= self.employee_id.user_id
        return res

    @api.multi
    def _check_can_review(self):
        super()._check_can_review()
        if self.filtered(
                lambda sheet: not sheet.can_review and
                sheet.review_policy == 'direct_manager'):
            raise UserError(_(
                'Only a employee\'s Direct Manager can review the sheet.'
            ))
