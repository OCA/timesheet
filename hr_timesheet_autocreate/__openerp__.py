# -*- coding: utf-8 -*-
######################################################################################################
#
# Copyright (C) B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

{
    'name': 'Timesheets Autocreate',
    'version': '1.0',
    'category': 'Generic Modules/Human Ressources',
    'description': """
        This module add a scheduler which create automatically timesheet records for all active employees for the last week. This avoids the employee to forget to confirm a timesheet when it did not open it for a full week and hence the record is not created automatically without this module.
    """,
    'author': 'BHC',
    'website': 'www.bhc.be',
    'depends': ['base','hr_timesheet_sheet','BHC_day_off','hr_holidays'],
    'init_xml': [],
    'update_xml': ['scheduled_timesheet.xml',
                   'day_off.xml',
                   'holiday_view.xml',
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
