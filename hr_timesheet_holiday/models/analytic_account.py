# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AnalyticAccount(models.Model):
    """Add 'is_leave_account' flag to Analytic Account"""
    _inherit = 'account.analytic.account'

    is_leave_account = fields.Boolean(
        'Leaves',
        help="Check this field if this account manages leaves",
        default=False,
    )
    holiday_status_ids = fields.One2many(
        comodel_name='hr.holidays.status',
        inverse_name='analytic_account_id',
    )

    @api.model
    def _trigger_project_creation(self, vals):
        if vals.get('is_leave_account'):
            return True
        return super(AnalyticAccount, self)._trigger_project_creation(vals)

    @api.multi
    def project_create(self, vals):
        res = super(AnalyticAccount, self).project_create(vals)
        if isinstance(res, (int, float)):
            for aa in self:
                if aa.is_leave_account:
                    project = self.env['project.project'].browse(res)
                    project.write({'allow_timesheets': True})
        return res

    @api.constrains('is_leave_account', 'project_ids')
    @api.multi
    def _check_account_allow_timesheet(self):
        for aa in self:
            if any(project.allow_timesheets is False
                   for project in aa.project_ids):
                raise ValidationError(
                    _('All the projects for the analytic '
                      'account must allow timesheets.'))
