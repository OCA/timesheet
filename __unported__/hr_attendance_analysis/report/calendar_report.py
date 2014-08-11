# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class Parser(report_sxw.rml_parse):

    def _get_day_of_week(self, day):
        WEEKDAYS = {
            0: _('Monday'),
            1: _('Tuesday'),
            2: _('Wednesday'),
            3: _('Thursday'),
            4: _('Friday'),
            5: _('Saturday'),
            6: _('Sunday'),
        }
        weekday = datetime.strptime(day, DEFAULT_SERVER_DATE_FORMAT).weekday()
        return WEEKDAYS[weekday]

    def _get_month_name(self, day):
        str_month = ''
        month = datetime.strptime(day, DEFAULT_SERVER_DATE_FORMAT).month
        if month == 1:
            str_month = _('January')
        elif month == 2:
            str_month = _('February')
        elif month == 3:
            str_month = _('March')
        elif month == 4:
            str_month = _('April')
        elif month == 5:
            str_month = _('May')
        elif month == 6:
            str_month = _('June')
        elif month == 7:
            str_month = _('July')
        elif month == 8:
            str_month = _('August')
        elif month == 9:
            str_month = _('September')
        elif month == 10:
            str_month = _('October')
        elif month == 11:
            str_month = _('November')
        elif month == 12:
            str_month = _('December')
        return str_month

    def _get_days_by_employee(self, employee_id):
        form = self.localcontext['data']['form']
        return form['days_by_employee'][str(employee_id)]

    def _get_totals_by_employee(self, employee_id):
        form = self.localcontext['data']['form']
        return form['totals_by_employee'][str(employee_id)]

    def _get_max_per_day(self):
        form = self.localcontext['data']['form']
        return form['max_number_of_attendances_per_day']

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'days_by_employee': self._get_days_by_employee,
            'totals_by_employee': self._get_totals_by_employee,
            'day_of_week': self._get_day_of_week,
            'max_per_day': self._get_max_per_day,
            'month_name': self._get_month_name,
        })

report_sxw.report_sxw('report.attendance_analysis.calendar_report',
                      'attendance_analysis.calendar_report',
                      'attendance_analysis/report/calendar_report.mako',
                      parser=Parser)
