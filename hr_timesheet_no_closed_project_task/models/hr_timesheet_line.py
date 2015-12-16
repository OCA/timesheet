# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


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
