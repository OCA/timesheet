# -*- coding: utf-8 -*-
# Authors: Laurent Mignon
# Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class HRTimesheetReport(models.Model):
    _inherit = "hr.timesheet.report"
    _name = "hr.timesheet.report"

    task_id = fields.Many2one('project.task', string='Task', readonly=True)

    def _select(self):
        select_str = super(HRTimesheetReport, self)._select()
        select_str += ", aal.task_id as task_id"
        return select_str

    def _group_by(self):
        group_by_str = super(HRTimesheetReport, self)._group_by()
        group_by_str += ", aal.task_id"
        return group_by_str
