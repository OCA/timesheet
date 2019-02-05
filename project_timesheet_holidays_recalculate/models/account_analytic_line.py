# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api

import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def action_recalculate_timesheet_from_leave(self):
        for line in self.filtered('holiday_id'):
            work_hours_data = line.employee_id.list_work_time_per_day(
                line.holiday_id.date_from,
                line.holiday_id.date_to,
            )
            _logger.info('!!!! %s %s %s => %s', line.employee_id, line.holiday_id.date_from, line.holiday_id.date_to, work_hours_data)
            for day_date, work_hours_count in work_hours_data:
                if day_date != line.date:
                    continue

                _logger.info('!!!! %s => %s', day_date, work_hours_count)

                line.unit_amount = work_hours_count
                break
