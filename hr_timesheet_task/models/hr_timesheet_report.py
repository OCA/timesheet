# -*- coding: utf-8 -*-
# Copyright 2017 Scopea, Niboo SPRL, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrTimesheetReport(models.Model):
    _inherit = 'hr.timesheet.attendance.report'

    task_id = fields.Many2one('project.task', 'Task', readonly=True)

    def _select(self):
        return '%s,aal.task_id' % super(HrTimesheetReport, self)._select()

    def _group_by(self):
        return '%s,task_id' % super(HrTimesheetReport, self)._group_by()

