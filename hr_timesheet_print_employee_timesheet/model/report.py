# -*- coding: utf-8 -*-
# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_pdf(
        self, cr, uid, ids, report_name, html=None, data=None, context=None
    ):
        if report_name == (
                'hr_timesheet_print_employee_timesheet.'
                'qweb_hr_analytical_timesheet_employees'
        ):
            context = dict(context or {}, landscape=True)

        return super(Report, self).get_pdf(
            cr, uid, ids, report_name, html=html, data=data, context=context,
        )
