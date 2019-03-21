# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.constrains('project_id', 'employee_id')
    def _check_employee_id(self):
        if config['test_enable'] and not self.env.context.get(
                'test_hr_timesheet_employee_required'):
            return

        for line in self:
            if line.project_id and not line.employee_id:
                raise ValidationError(_('Employee is required for Task Log'))
