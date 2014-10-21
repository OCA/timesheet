# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
{
    'name': 'Notify managers and timesheet users of submissions and approvals',
    'version': '1.0',
    'author': 'Therp BV',
    'complexity': 'normal',
    'category': 'Human Resources',
    'description': """
Module purpose
==============
Subscribe managers to the timesheets of their users automatically. Inform
managers of comments and submissions, while informing users of approvals
and rejections.

Known issues
============
While rejections of timesheets by the manager are logged, on a technical
level this is only a reset to draft status. Therefore,
a rejection cannot be distinguished from a newly created timesheet.
    """,
    'depends': [
        'hr_timesheet_sheet',
    ],
    'data': ['data/mail_message_subtype.xml'],
}
