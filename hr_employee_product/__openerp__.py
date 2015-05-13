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
    'name': "Manage products representing employees",
    'version': '1.0',
    'category': 'Warehouse Management',
    'description': """
Manage products representing employees
======================================

This module was written to extend the Timesheet capabilities of Odoo.

It allows to restrict the access to the products that represent an actual
employee, only to the Human Resources / Manager group.

A company may want to do that when they want to keep an actual hourly cost
per employee, so that the time entered by employees through timesheets can
result in a more realistic cost, but at the same time want to conceal this
information to general employees.


Installation
============

No additional installation instructions are required.


Configuration
=============

This module does not require any additional configuration.

Usage
=====

A user in the group 'Human Resources / Manager' should go to the product form
and set the checkbox 'Is Employee'. This product will then be accessible only
by this group.

Known issues / Roadmap
======================

No issues have been identified.

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
    'author': "Eficent, Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['product', 'hr_timesheet'],
    "data": [
        'view/product.xml',
        'security/product_security.xml'
    ],
    'test': [],
    "demo": [],
    "active": False,
    "installable": True
}
