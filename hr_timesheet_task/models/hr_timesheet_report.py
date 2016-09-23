# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# Copyright 2016 Niboo SPRL
from openerp import fields, models


class HrTimesheetReport(models.Model):
    _inherit = 'hr.timesheet.report'

    task_id = fields.Many2one(comodel_name='project.task', string='Task',
                              readonly=True)

    def _select(self):
        return '%s,aal.task_id' % super(HrTimesheetReport, self)._select()

    def _group_by(self):
        return '%s,task_id' % super(HrTimesheetReport, self)._group_by()
