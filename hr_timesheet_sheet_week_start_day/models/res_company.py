# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

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

    timesheet_week_start = fields.Selection(_WEEKDAYS,
                                            string='Week start day',
                                            default='0')
