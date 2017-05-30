.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============
Toggl connector
===============

This module allows you to connect to Toggl and read timesheets from there.

Configuration
=============

To configure this module, you need to:

#. Go to Connectors - Toggl - Backends
#. Create a new backend
#. Enter the Toggl API URL (currently `https://toggl.com/reports/api/v2/details`)
#. Enter your Toggl API key 
#. Enter the Toggl Workspace ID to import from (Click your workspace and look in the URL)

Usage
=====

To use this module, you need to:

# Make sure that employee names in Toggl are literally the same as in Odoo
# Make sure that project names in Toggl are literally the same as in Odoo
# Make sure that client names in Toggl are literally the same as in Odoo
# Go to an employee's timesheet in Odoo and click "Import from Toggl".

Features / Limitations
======================

* If there are multiple timesheet lines on the same day for same 
  employee, client, project and descriptions, they are added together
* Timesheet lines are rounded on 15 minute intervals
* If the project of a Toggl time entry is empty, it will look for a project named after the current company.
* If the client of a Toggl time entry is empty, it will look for projects belonging to the current company.

Known issues / Roadmap
======================

* Currently the import is manual for each timesheet. This allows for directly visible error messages,
  and conscious manual corrections to the timesheet data in Odoo. A next step could be to make the connector
  automatic. But then a usable error log needs to be placed somewhere to deal with the mismatches, and also
  a sync protocol needs to be thought out about how to deal with entries that have been changed in Odoo.
  Do we overwrite them, leave them as they are, or sync the changed ones back to Toggl?

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr_timesheet/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Tom Blauwendraat <info@sunflowerweb.nl>
* Dan Kiplangat <dan@sunflowerweb.nl>
* Terrence Nzaywa <terrence@sunflowerweb.nl>

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
