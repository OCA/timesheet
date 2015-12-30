# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services, S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR period create timesheet",
    "version": "7.0.1.0.0",
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Human Resources",
    "depends": ["hr_period", "hr_timesheet_sheet"],
    "description": """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
HR period create timesheet
==========================

This module allows to create Timesheet Sheets from HR Payroll Periods.


Usage
=====
To use this module, you need to:

Go to 'Human Resources / Configuration / Payroll / Payroll Periods'. Then
select a particular Payroll Period in the list view and press 'More >
Generate Timesheets'.
The application will propose to create a new timesheet for each employee of
the company, but you can remove employees as needed.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/117/7.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/117/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
117/issues/new?body=module:%20
hr_period_create_timesheet%0Aversion:%20
7.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A
%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jordi Ballester - Eficent Business and IT Consulting Services S.L. <jordi.ballester@eficent.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.

    """,
    "license": "AGPL-3",
    "data": [
        "wizards/hr_period_create_timesheet_view.xml",
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}
