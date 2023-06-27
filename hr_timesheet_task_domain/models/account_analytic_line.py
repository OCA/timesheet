# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    task_id = fields.Many2one(
        domain="project_id and [('company_id', '=', company_id), "
        "('project_id.allow_timesheets', '=', True), "
        "('stage_id.fold', '=', False), ('project_id', '=', project_id)] "
        "or [('company_id', '=', company_id), "
        "('project_id.allow_timesheets', '=', True), "
        "('project_id', '=?', project_id)]",
    )
