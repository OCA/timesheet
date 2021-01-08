# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    def _read_group_format_result(self, data, annotated_groupbys, groupby,
                                  groupby_dict, domain, context):
        if context.get('hr_timesheet_print_employee_timesheet_date_raw'):
            data['date:raw'] = data.get('date:day')
        data = super(HrAnalyticTimesheet, self)._read_group_format_result(
            data, annotated_groupbys, groupby, groupby_dict, domain, context)
        return data
