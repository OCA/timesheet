# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_invoice_hide_to_invoice,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_invoice_hide_to_invoice is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_invoice_hide_to_invoice is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_invoice_hide_to_invoice.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api

GROUP_ID = ('hr_timesheet_invoice_hide_to_invoice.'
            'group_invoice_rate_timesheet_line')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    to_invoice = fields.Many2one(groups=GROUP_ID)

    @api.model
    def check_field_access_rights(self, operation, fields):
        """Allow to modify to invoiced field to avoid to override all views"""
        if 'to_invoice' in fields and\
                not self.env['res.users'].has_group(GROUP_ID):
            fields.remove('to_invoice')
        res = super(AccountAnalyticLine, self)\
            .check_field_access_rights(operation, fields)
        return res

    @api.model
    def _add_default_to_invoice(self, vals):
        if not self.env['res.users'].has_group(GROUP_ID) and\
                vals.get('account_id'):
            account_id = vals.get('account_id')
            account = self.env['account.analytic.account'].browse([account_id])
            vals['to_invoice'] = account.to_invoice.id

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        self._add_default_to_invoice(vals)
        return super(AccountAnalyticLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self._add_default_to_invoice(vals)
        return super(AccountAnalyticLine, self).write(vals)
