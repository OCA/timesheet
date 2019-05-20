# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import _, api, models, fields
from openerp.exceptions import Warning as UserError


class HrAnalyticTimesheet(models.Model):
    """Link leave requests to analytic timesheet entries"""
    _inherit = 'hr.analytic.timesheet'

    leave_id = fields.Many2one('hr.holidays', 'Leave id')

    @api.multi
    def unlink(self):
        leaves = self.mapped('leave_id')
        if leaves and set(leaves.mapped('state')) - set([
                'draft', 'cancel', 'refuse',
        ]):
            raise UserError(_(
                "You can't delete timesheet lines with active leaves",
            ))
        return super(HrAnalyticTimesheet, self).unlink()
