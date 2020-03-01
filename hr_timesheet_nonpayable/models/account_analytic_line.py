# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    is_nonpayable = fields.Boolean(
        string='Non-payable',
    )
    nonpayable_amount = fields.Monetary(
        string='Non-payable Amount',
        default=0.0,
    )

    @api.model
    def create(self, vals):
        if 'is_nonpayable' not in vals and 'project_id' in vals:
            project = self.env['project.project'].browse(vals['project_id'])
            vals['is_nonpayable'] = project.is_nonpayable
        if 'amount' in vals and vals.get('is_nonpayable'):
            vals['nonpayable_amount'] = vals['amount']
            vals['amount'] = 0.0
        return super().create(vals)

    @api.multi
    def write(self, vals):
        if self.env.context.get('nonpayable_bypass'):
            return super().write(vals)

        if 'amount' in vals and 'is_nonpayable' not in vals:
            nonpayable_aal = self.filtered('is_nonpayable')
            return super(AccountAnalyticLine, nonpayable_aal).write({
                **vals,
                'amount': 0.0,
                'nonpayable_amount': vals['amount'],
            }) and super(AccountAnalyticLine, self - nonpayable_aal).write(
                vals
            )

        res = super().write(vals)
        if not res or 'is_nonpayable' not in vals:
            return res
        nonpayable_aal = self.filtered('is_nonpayable')
        for aal in nonpayable_aal:
            aal.with_context(nonpayable_bypass=True).write({
                'amount': 0.0,
                'nonpayable_amount': aal.amount or 0.0,
            })
        for aal in (self - nonpayable_aal):
            aal.with_context(nonpayable_bypass=True).write({
                'amount': aal.nonpayable_amount or 0.0,
                'nonpayable_amount': 0.0,
            })
        return True

    @api.onchange('is_nonpayable')
    def onchange_is_nonpayable(self):
        self.amount = 0.0 if self.is_nonpayable else self.nonpayable_amount
