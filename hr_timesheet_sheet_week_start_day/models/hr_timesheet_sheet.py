# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrTimesheetSheet(models.Model):

    _inherit = "hr_timesheet_sheet.sheet"

    @api.model
    def _default_date_from(self):
        date_from = super(HrTimesheetSheet, self)._default_date_from()
        user = self.env.user
        r = user.company_id.timesheet_range or 'month'
        if r == 'week':
            if user.company_id.timesheet_week_start:
                datetime_from = (datetime.today() + relativedelta(
                    weekday=int(user.company_id.timesheet_week_start),
                    days=-6))
                date_from = fields.Date.to_string(datetime_from)
        return date_from

    @api.model
    def _default_date_to(self):
        date_to = super(HrTimesheetSheet, self)._default_date_to()
        user = self.env.user
        r = user.company_id.timesheet_range or 'month'
        week_end = (int(user.company_id.timesheet_week_start) + 6) % 7
        if r == 'week':
            datetime_to = (datetime.today() + relativedelta(
                weekday=week_end))
            date_to = fields.Date.to_string(datetime_to)

        return date_to

    date_from = fields.Date(default=_default_date_from)
    date_to = fields.Date(default=_default_date_to)
