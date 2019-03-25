.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
HR Timesheet Sheet
==================

This module supplies a new screen enabling you to manage your work encoding (timesheet) by period.
Timesheet entries are made by employees each day. At the end of the defined period,
employees validate their sheet and the manager must then approve his team's entries.
Periods are defined in the company forms and you can set them to run monthly, weekly or daily.

Installation
============

This module relies on:

* The OCA module '2D matrix for x2many fields', and can be downloaded from
  Github: https://github.com/OCA/web/tree/11.0/web_widget_x2many_2d_matrix


Configuration
=============

If you want other default ranges different from weekly, you need to go:

* In the menu `Configuration` -> `Settings` -> **Timesheet Options**,
  and select in **Timesheet Sheet Range** the default range you want.
* When you have a weekly range you can also specify the **Week Start Day**.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/117/11.0

Known issues / Roadmap
======================

* When you change values on the `Summary` tab, a save should be performed
  to ensure the data shown on the `Details` tab is correct. This limitation could be
  perhaps avoided by including a .js file that aligns the `Details` tab.
* The timesheet grid is limited to display a max. of 1M cells, due to a
  limitation of the tree view limit parameter not being able to dynamically
  set a limit. Since default value of odoo, 40 records is too small, we decided
  to set 1M, which should be good enough in the majority of scenarios.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr-timesheet/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Miquel Raïch <miquel.raich@eficent.com>
* Andrea Stirpe <a.stirpe@onestein.nl>
* Lois Rilo <lois.rilo@eficent.com>

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
