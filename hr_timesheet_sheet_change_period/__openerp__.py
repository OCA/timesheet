# -*- coding: utf-8 -*-
##############################################################################
#
# This file is part of hr_timesheet_sheet_change_period,
# an Odoo module.
#
# Authors: ACSONE SA/NV (<http://acsone.eu>)
#
# hr_timesheet_sheet_change_period is free software:
# you can redistribute it and/or modify it under the terms of the GNU
# Affero General Public License as published by the Free Software
# Foundation,either version 3 of the License, or (at your option) any
# later version.
#
# hr_timesheet_sheet_change_period is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with hr_timesheet_sheet_change_period.
# If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'HR Timesheet Change Period',
    'summary': """
Allows to change covered period while the timesheet is in the 'draft' state""",
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'http://www.acsone.eu',
    'category': 'Human Resources',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet_sheet',
    ],
    'images': [
    ],
    'data': [
        'wizard/hr_timesheet_sheet_change_period.xml',
        'views/hr_timesheet_sheet_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
        'hr_timesheet_sheet_change_period_demo.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
