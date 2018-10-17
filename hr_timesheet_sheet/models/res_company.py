# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from dateutil.rrule import (MONTHLY, WEEKLY, DAILY)

_WEEKDAYS = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday')
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    sheet_range = fields.Selection([
        (MONTHLY, 'Month'),
        (WEEKLY, 'Week'),
        (DAILY, 'Day')],
        string='Timesheet Sheet Range',
        default=WEEKLY,
        help="The range of your Timesheet Sheet.")

    timesheet_week_start = fields.Selection(
        selection=_WEEKDAYS,
        string='Week start day',
        default='0')
