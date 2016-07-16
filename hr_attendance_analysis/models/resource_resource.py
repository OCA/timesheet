# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-15 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"
    tolerance_from = fields.Float(
        'Tolerance from',
        size=8,
        help='Sign out done in the interval "Work to - Tolerance from" '
        'will be considered done at "Work to"',
    )
    tolerance_to = fields.Float(
        'Tolerance to',
        size=8,
        help='Sign in done in the interval "Work from + Tolerance to" '
        'will be considered done at "Work from"',
    )


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"
    attendance_rounding = fields.Selection(
        selection=[
            ('60', '1'),
            ('30', '2'),
            ('20', '3'),
            ('12', '5'),
            ('10', '6'),
            ('7.5', '8'),
            ('6', '10'),
            ('5', '12'),
            ('4', '15'),
            ('3', '20'),
            ('2', '30'),
            ('1', '60')],
        string='Attendance rounding',
        help='For instance, using rounding = 15 minutes, every sign in '
        'will be rounded to the following quarter hour and every '
        'sign out to the previous quarter hour',
    )
    overtime_rounding = fields.Selection(
        selection=[
            ('60', '1'),
            ('30', '2'),
            ('20', '3'),
            ('12', '5'),
            ('10', '6'),
            ('7.5', '8'),
            ('6', '10'),
            ('5', '12'),
            ('4', '15'),
            ('3', '20'),
            ('2', '30'),
            ('1', '60')],
        string='Overtime rounding',
        help='Setting rounding = 30 minutes, an overtime of 29 minutes '
        'will be considered as 0 minutes, 31 minutes as 30 minutes, '
        '61 minutes as 1 hour and so on',
    )
    overtime_rounding_tolerance = fields.Float(
        string='Overtime rounding tolerance',
        size=8,
        help='Overtime can be rounded using a tolerance. Using tolerance '
        '= 3 minutes and rounding = 15 minutes, if employee does '
        'overtime of 12 minutes, it will be considered as 15 '
        'minutes.',
    )
    leave_rounding = fields.Selection(
        selection=[
            ('60', '1'),
            ('30', '2'),
            ('20', '3'),
            ('12', '5'),
            ('10', '6'),
            ('7.5', '8'),
            ('6', '10'),
            ('5', '12'),
            ('4', '15'),
            ('3', '20'),
            ('2', '30'),
            ('1', '60')],
        string='Leave rounding',
        help='On the contrary of overtime rounding, using rounding = 15 '
        'minutes, a leave of 1 minute will be considered as 15 '
        'minutes, 16 minutes as 30 minutes and so on',
    )
    overtime_type_ids = fields.One2many(
        comodel_name='resource.calendar.overtime.type',
        inverse_name='calendar_id',
        string='Overtime types',
    )


class ResourceCalendarOvertimeRange(models.Model):
    _name = 'resource.calendar.overtime.type'
    _description = 'Overtime type'
    _order = 'sequence'

    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    name = fields.Char(
        string='Type Description',
        size=64,
        required=True,
    )
    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        string='Calendar',
    )
    limit = fields.Float(
        string='Limit',
        size=8,
        help='Limit, in hours, of overtime that can be imputed to this '
        'type of overtime in a day. The surplus is imputed to the '
        'subsequent type',
    )
