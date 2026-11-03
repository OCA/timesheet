# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTimeType(models.Model):
    _name = "project.time.type"
    _description = "Define Time Types"

    name = fields.Char(required=True)
    code = fields.Char()
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        index=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
