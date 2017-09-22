.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

Manage products representing employees
======================================

This module was written to extend the Timesheet capabilities of Odoo.

It allows to restrict the access to the products that represent an actual
employee, only to the Human Resources / Manager group.

A company may want to record an actual hourly cost per employee, so that the
time entered by employees through timesheets can result in a more realistic
cost, but at the same time want to conceal this information to general
employees.

Usage
=====

A user in the group 'Human Resources / Manager' should go to the product form
and set the checkbox 'Is Employee'. This product will then be accessible only
by this group.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/117/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr-timesheet/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>
* Aaron Henriquez <ahenriquez@eficent.com>

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