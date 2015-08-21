# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_invoice_hide_to_invoice,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_invoice_hide_to_invoice is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_invoice_hide_to_invoice is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_invoice_hide_to_invoice.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "HR Timesheet Invoice Hide To Invoice",

    'summary': """
        Adding a security group to display invoicing rate field on timesheet
        line""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Invoicing & Payments',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet_invoice',
    ],
    'data': [
        'security/hr_timesheet_invoice_hide_to_invoice_security.xml',
        'views/hr_analytic_timesheet_view.xml',
    ],
}
