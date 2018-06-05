.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Link holidays to analytic lines
===============================

This module adds a relation between Leave Type and Analytic Account.
When a Leave Request is granted, the granted days are converted to hours and
added as a line to the Analytic Account. Conversely, when a timesheet line
with an analytic account pointed to by a Leave Type is approved, this will
result in an approved leave request.

When the leave is revoked, the analytic lines are removed again.

The analytic lines are read-only, so you cannot edit them directly, just by
granting or revoking leave requests.

The hours to input per day is configurable at company level.

Limitations:

- Consider that the work days are Monday to Friday

Configuration
=============

To configure this module, you need to:

#. Find your company in Settings - Companies and configure the amount of hours
   per workday under Configuration - Timesheets - Timesheet Hours Per Day.
#. For each Leave Type under Human Resources - Leave Types, select or create
   an Analytic Account.

Usage
=====

To use this module, you need to:

#. Approve a Leave Request
#. See the hours added to Timesheet Activities
#. Revoke a Leave Request
#. See the hours removed from Timesheet Activities

Known issues / Roadmap
======================

* Hours per workday should be configurable per employee, not only by company.
  To make this easier, the function `_get_hours_per_day` was made which can be
  overridden by child modules.
* We should probably start using resource calendars.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr-timesheet/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Tom Blauwendraat <tom@sunflowerweb.nl>
* Terrence Nzaywa <terrence@sunflowerweb.nl>
* Holger Brunn <hbrunn@therp.nl>

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
