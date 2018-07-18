# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrHolidaysStatus(models.Model):
    """Add project to holiday status"""
    _inherit = 'hr.holidays.status'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        related='project_id.analytic_account_id',
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )
