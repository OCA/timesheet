# Copyright 2024 Tecnativa - Juan José Seguí
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TimesheetPredefinedDescription(models.Model):
    _name = "timesheet.predefined.description"
    _description = "Predefined Description for Timesheets"

    name = fields.Char(string="Description", required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
