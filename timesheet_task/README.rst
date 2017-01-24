.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Analytic Timesheet In Task
==========================

Replace task work items (``project.task.work``) linked to task with
timesheet lines (``hr.analytic.timesheet``).

Unlike the module project_timesheet, it allows to have only one single
object that handles and records time spent by employees, making more
coherence for the end user. This way, time entered through timesheet
lines or tasks is the same. As long as a timesheet lines has an
associated task, it will compute the related indicators.

Used with the module hr_timesheet_task, it also allows users to complete
task information through the timesheet sheet (``hr.timesheet.sheet``).

Version 1.0.0 restores the ability to record the work date and time,
just you could with the original Task Work lines

It also makes available a scheduler action to migrate the old Task Work lines
into Timesheet lines, so that work history can be made available.

This process can be run in the background,
so that a large amount of lines can be converted by a long running
process and the still have the Odoo serevr available for the end users.
In case the process in interrupted (for example, because
the cron worker is killed), running the migration again will continue
with the lines not yet migrated.
Work Lines for Users that are not properly setup (don't have an
Employee with a Product and a Journal configured) will display warnings
in the server log, and will be skipped. The migration cron job will
continuously try to migrate them, so it should be disabled
when no more migration work is needed.


Installation
============

Version 1.0.0 add the ``project_timesheet`` dependency.
Make sure you install it before performing the upgrade.


Configuration
=============

The data migration scheduler task is deisbled by default.
If you need it, make sure you enable in the Scheduled Actions technical menu.
Keep an eye on the server log to see the migration progress and warning messages.
You can disable it again once the migration work has been completed.


Usage
=====

To use this module, you need to:

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/117/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Firstname Lastname <email.address@example.org>
* Second Person <second.person@example.org>

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
