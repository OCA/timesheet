# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def action_timesheet_report_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.timesheet.report.wizard',
            'views': [[False, 'form']],
            'target': 'new',
            'context': {
                'default_line_ids': [(6, False, self.ids)],
            },
        }
