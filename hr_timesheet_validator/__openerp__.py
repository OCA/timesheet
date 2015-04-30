# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              Eficent <contact@eficent.com>
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
    'name': 'Timesheet validators',
    'version': '1.0',
    'author': 'Eficent',
    'category': 'Human Resources',
    'description': """
Timesheet validators
====================
This module was written to extend the HR Timesheet capabilities of Odoo.

Timesheets in Odoo can be validated by users belonging to the group
“Human Resources / Officer”.

However it is frequent for companies allow to employees outside of the
Human Resources group to validate timesheet.

This module allows a user outside of the Human Resources groups to validate
timesheets. A rule is predefined, but it is flexible enough to accept
extensions.

Installation
============

No additional installation instructions are required.


Configuration
=============

This module does not require any additional configuration.

Usage
=====

At the time when a user submits a timesheet to the Manager, the application
determines the validators.

Only those validators or employees in the group of Human Resources Officer
are capable of approving the timesheet.

The current rule sets as validators of a timesheet:

- The head of the department that the employee belongs to

In case that the employee is head of the department, it will attempt to add
the head of the parent department instead.

- The employee’s direct manager

The list of validators is visible in the employee’s timesheet.


Known issues / Roadmap
======================

No issue has been identified.

Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>

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
    'website': 'http://www.eficent.com',
    'depends': ['hr_timesheet_sheet'],
    'data': [
        'security/hr_timesheet_sheet_security.xml',
        'view/hr_timesheet_sheet_view.xml',
        'view/hr_timesheet_workflow.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
