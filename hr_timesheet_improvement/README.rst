.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Timesheet improvements
======================

Modifies timesheet behavior:
 * Ensure a DESC order on timesheet lines
 * Set default date for manually entering attendance to max attendance date
 * Redefine constraint on timesheets to check alternation of 'sign in' and
   'sign out' only on current timesheet instead of doing it on all timesheets
   of the employee

Configuration
=============

To configure this module, you need to:

* Go To Settings -> Users -> Users -> admin -> Access rights -> Technical Settings , And activate "Attendances" checkbox

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/117/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr-timesheet/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/hr-timesheet/issues/new?body=module:%20hr_timesheet_improvement%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Vincent Renaville <vincent.renaville@camptocamp.com>
* Charbel Jacquin <charbel.jacquin@camptocamp.com>
* Damien Crier <damien.crier@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

