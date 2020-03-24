# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    unpaid = fields.Boolean(
        related='holiday_id.holiday_status_id.unpaid',
        store=True,
    )
