.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=============
CRM Timesheet
=============

This module allows to generate timesheets from leads/opportunities and phone
calls.


Usage
=====

* In lead/opportunity forms you have Timesheet tab.
* In phone calls tree, you can add an analytic account, and if the call has
  any duration, a timesheet activity will be created.
* You can choose how to input time: (1) set time you dedicated to call after
  finishing it OR (2) create & save call with time set in 00:00 and Stop the
  timer when call ends, this will set exactly the time you spent.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/117/8.0


Known issues / Roadmap
======================

* crm.phonecall::write() method has to be wrapped by api.one and this could
  affect performance when writing lot of records at the same time.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr-timesheet/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/hr-timesheet/issues/new?body=module:%20crm_timesheet%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


License
=======

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/agpl-3.0-standalone.html>.


Credits
=======

Contributors
------------

* Antonio Espinosa <antonioea@antiun.com>
* Rafael Blasco <rafabn@antiun.com>
* Javier Iniesta <javieria@antiun.com>

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