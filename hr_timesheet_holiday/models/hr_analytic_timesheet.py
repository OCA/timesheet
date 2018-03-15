# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class HrAnalyticTimesheet(models.Model):
    """Link leave requests to analytic timesheet entries"""
    _inherit = 'hr.analytic.timesheet'

    leave_id = fields.Many2one('hr.holidays', 'Leave id')
