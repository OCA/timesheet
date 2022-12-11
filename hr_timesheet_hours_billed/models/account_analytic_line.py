# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    approved = fields.Boolean(default=False, inverse="_inverse_approved")
    approved_user_id = fields.Many2one(
        "res.users",
        string="Approved by",
        index=True,
        tracking=True,
        readonly=True,
    )
    approved_date = fields.Datetime(copy=False, readonly=True)
    unit_amount_billed = fields.Float(string="Hours Billed")

    # set approved_user_id and date if approved state change
    def _inverse_approved(self):
        user = self.env.user
        now = fields.Datetime.now()
        for record in self.filtered(lambda rec: rec.approved):
            record.write({"approved_date": now, "approved_user_id": user})

    # override create method to initialize unit_amount_billed
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("unit_amount_billed"):
                vals["unit_amount_billed"] = vals.get("unit_amount", 0.0)
        return super(AccountAnalyticLine, self).create(vals_list)

    def action_approve_records(self):
        self.filtered(lambda rec: not rec.approved).write({"approved": True})

    def action_decline_records(self):
        self.filtered(lambda rec: rec.approved).write({"approved": False})
