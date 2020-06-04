# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTimeType(models.Model):
    _name = "project.time.type"
    _description = "Define Time Types"

    name = fields.Char(
        string='Name',
        required=True
    )
    code = fields.Char(
        string='Code',
    )
    description = fields.Text(
        string='Description'
    )
