# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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

from openerp.osv import fields, orm

class resource_calendar_attendance(orm.Model):
    _inherit = "resource.calendar.attendance"
    _columns = {
        'tolerance_from': fields.float('Tolerance from', size=8,
            help='Sign out done in the interval "Work to - Tolerance from" will be considered done at "Work to"'),
        'tolerance_to': fields.float('Tolerance to', size=8,
            help='Sign in done in the interval "Work from + Tolerance to" will be considered done at "Work from"'),
        }
    

class resource_calendar(orm.Model):
    _inherit = "resource.calendar"
    _columns = {
        'attendance_rounding': fields.selection([
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
            ('1', '60'),
            ],
            'Attendance rounding', help='For instance, using rounding = 15 minutes, every sign in will be rounded to the following quarter hour and every sign out to the previous quarter hour'),
        #'attendance_rounding': fields.float('Attendance rounding', size=8,
            #help='For instance, using rounding = 15 minutes, every sign in will be rounded to the following quarter hour and every sign out to the previous quarter hour'),
        'overtime_rounding': fields.selection([
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
            ('1', '60'),
            ],
            'Overtime rounding',
            help='Setting rounding = 30 minutes, an overtime of 29 minutes will be considered as 0 minutes, 31 minutes as 30 minutes, 61 minutes as 1 hour and so on'),
        'overtime_rounding_tolerance': fields.float('Overtime rounding tolerance', size=8,
            help='Overtime can be rounded using a tolerance. Using tolerance = 3 minutes and rounding = 15 minutes, if employee does overtime of 12 minutes, it will be considered as 15 minutes.'),
        'leave_rounding': fields.selection([
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
            ('1', '60'),
            ],
            'Leave rounding',
            help='On the contrary of overtime rounding, using rounding = 15 minutes, a leave of 1 minute will be considered as 15 minutes, 16 minutes as 30 minutes and so on'),
        'overtime_type_ids': fields.one2many('resource.calendar.overtime.type', 'calendar_id', 'Overtime types'),
        }

class resource_calendar_overtime_range(orm.Model):
    _name = 'resource.calendar.overtime.type'
    _description = 'Overtime type'
    _order = 'sequence'
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Type Description', size=64, required=True),
        'calendar_id': fields.many2one('resource.calendar', 'Calendar'),
        'limit': fields.float('Limit', size=8,
            help='Limit, in hours, of overtime that can be imputed to this type of overtime in a day. The surplus is imputed to the subsequent type')
        }
