# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012 Camptocamp SA
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

import time
from datetime import datetime
from openerp.report import report_sxw


class timesheet_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(timesheet_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'format_date': self._get_and_change_date_format_for_swiss,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        self.localcontext['ts_lines'] = objects
        self.localcontext['tot_hours'] = self._get_tot_hours(objects)
        super(timesheet_report, self).set_context(
            objects, data, ids, report_type)

    def _get_tot_hours(self, ts_lines):
        tot = 0.0
        deduced = 0.0
        for line in ts_lines:
            if line.product_uom_id:
                factor = line.product_uom_id.factor
                if factor == 0.0:
                    factor = 1.0
            else:
                factor = 1.0
            factor_invoicing = 1.0
            if line.to_invoice and line.to_invoice.factor != 0.0:
                factor_invoicing = 1.0 - line.to_invoice.factor / 100
            if factor_invoicing > 1.0:
                deduced += ((line.unit_amount / factor) * factor_invoicing)
                tot += ((line.unit_amount / factor) * factor_invoicing)
            elif factor_invoicing <= 1.0:
                tot += (line.unit_amount / factor)
                deduced += ((line.unit_amount / factor) * factor_invoicing)
        return {'total': tot, 'deduced': deduced}

    def _get_and_change_date_format_for_swiss(self, date_to_format):
        date_formatted = ''
        if date_to_format:
            date_formatted = datetime.strptime(
                date_to_format, '%Y-%m-%d').strftime('%d.%m.%Y')
        return date_formatted

report_sxw.report_sxw(
    'report.hr.analytic.timesheet.report', 'hr.analytic.timesheet',
    'addons/hr_timesheet_print/report/timesheet_report.rml',
    parser=timesheet_report)
report_sxw.report_sxw(
    'report.analytic.line.timesheet.report', 'account.analytic.line',
    'addons/hr_timesheet_print/report/timesheet_report.rml',
    parser=timesheet_report)
