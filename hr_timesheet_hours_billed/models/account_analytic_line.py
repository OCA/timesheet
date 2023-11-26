# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    approved = fields.Boolean(inverse="_inverse_approved")
    approved_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Approved by",
        index=True,
        tracking=True,
        readonly=True,
    )
    approved_date = fields.Datetime(copy=False)
    unit_amount_billed = fields.Float(string="Hours Billed")

    # set approved_user_id and date if approved state change
    def _inverse_approved(self):
        self.filtered(lambda rec: rec.approved).write(
            {
                "approved_date": fields.Datetime.now(),
                "approved_user_id": self.env.user.id,
            }
        )

    # override create method to initialize unit_amount_billed
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("unit_amount_billed"):
                vals.update(unit_amount_billed=vals.get("unit_amount", 0.0))
        return super().create(vals_list)

    def action_toggle_approve_records(self, state):
        """
        Action toggle approve
        :param state: approve
        :return: None
        """
        self.filtered(lambda rec: not state == rec.approved).write({"approved": state})
