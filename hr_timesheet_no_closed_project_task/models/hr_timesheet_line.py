# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_no_closed_project_task,
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
#     along with hr_timesheet_no_closed_project_task.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class HrAnalyticTimesheet(models.Model):
    _inherit = "hr.analytic.timesheet"
    _name = "hr.analytic.timesheet"

    @api.multi
    def on_change_account_id(self, account_id, user_id=False):
        res = super(HrAnalyticTimesheet, self)\
            .on_change_account_id(account_id=account_id, user_id=user_id)
        if res.get('value') and res['value'].get('task_id'):
            task_id = res['value']['task_id']
            task = self.env['project.task'].browse([task_id])
            if task.stage_id.closed:
                res['value'].pop('task_id')
        return res
