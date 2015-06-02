Allows to change the period of a time sheet while it is unconfirmed
===================================================================

This module was written to extend the functionality of hr_timesheet_sheet to support the change of the timesheet period while the state is "Open".
The goal is to offer an alternative to the removal/recreation of the entire timesheet avoiding to loose all the lines just to fix a wrong or incomplete period.

Why a wizard to do this ?
To be sure that no unsaved data exists in the sheet (e.g. timesheet lines freshly added) form before changing the period.

Credits
=======

Contributors
------------

* Olivier Laurent (<olivier.laurent@acsone.eu>)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.
