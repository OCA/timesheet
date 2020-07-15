# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    allow_timesheet_for = fields.Selection(
        [('anyone', 'Anyone'),
         ('self', 'Self'),
         ('subordinates_only', 'Subordinates only'),
         ('self_and_subordinates', 'Self and Subordinates')],
        string="Can enter timesheet for")
