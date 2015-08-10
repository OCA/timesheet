# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
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

{
    'name': "HR Timesheet Sheet based on Payroll Period",
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
HR Timesheet Sheet based on Payroll Period
==========================================

This module was written to extend the human resources capabilities of Odoo,
and allows to create timesheets with start and end dates matching with the
payroll period.


Installation
============

This module depends on module 'hr_period', found in OCA 'hr' repository.
See: https://github.com/OCA/hr

Configuration
=============

Create first the Payroll Fiscal Years and Payroll
Periods from 'Human Resources > Configuration > Payroll'

Usage
=====
When the user goes to 'Human Resources > Time Tracking > My current
timesheet', the application will attempt to create a new timesheet using as
start and end dates the Pay Period corresponding to today's date.

Known issues / Roadmap
======================

No issues have been identified.

Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
""",
    'author': "Eficent,Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['hr_period'],
    "data": [],
    'test': [],
    "demo": [],
    "active": False,
    "installable": True
}
