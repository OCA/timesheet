# Copyright 2025 Miquel Pascual López(APSL-Nagarro)<mpascual@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTimeType(models.Model):
    _inherit = "project.time.type"

    non_billable = fields.Boolean(default=False)
