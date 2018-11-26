# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api

import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def action_reset_user_from_employee(self):
        self._reset_user_from_employee()

        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.multi
    def action_reset_user_from_employee_all(self):
        self.search([
            ('employee_id','!=',False)
        ])._reset_user_from_employee()

        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.multi
    def _reset_user_from_employee(self):
        _logger.info('Resetting users from employees')

        for line in self:
            if not line.employee_id.id:
                continue

            line.write({
                'user_id': line.employee_id.user_id.id,
            })

            _logger.info(
                'Resetting user %s from employee %s on "%s"',
                line.employee_id.name,
                line.user_id.name,
                line.name
            )
