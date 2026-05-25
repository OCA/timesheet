# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    # Python Logic Added: Added a model override for account.analytic.line to
    # explicitly set timesheet_invoice_id as readonly=False. This is necessary
    # because Odoo 19's ORM is stricter about enforcing readonly constraints
    # defined in the Python layer, which would otherwise prevent the
    # XML-level readonly="False" from working.
    timesheet_invoice_id = fields.Many2one(
        readonly=False,
    )
