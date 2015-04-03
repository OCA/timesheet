
# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laurent Mignon
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models


class hr_timesheet_report(models.Model):
    _inherit = "hr.timesheet.report"
    _name = "hr.timesheet.report"

    task_id = fields.Many2one('project.task', string='Task', readonly=True)

    def _select(self):
        select_str = super(hr_timesheet_report, self)._select()
        select_str += ", aal.task_id as task_id"
        return select_str

    def _group_by(self):
        group_by_str = super(hr_timesheet_report, self)._group_by()
        group_by_str += ", aal.task_id"
        return group_by_str
