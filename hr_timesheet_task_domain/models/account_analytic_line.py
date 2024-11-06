# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.project.models.project_task import CLOSED_STATES


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    task_id = fields.Many2one(
        domain="project_id and [('company_id', 'in', (company_id, False)), "
        "('project_id.allow_timesheets', '=', True), "
        "('state', 'not in', " + str(list(CLOSED_STATES.keys())) + "), "
        "('project_id', '=', project_id)] "
        "or [('company_id', 'in', (company_id, False)), "
        "('project_id.allow_timesheets', '=', True), "
        "('project_id', '=?', project_id)]",
    )
