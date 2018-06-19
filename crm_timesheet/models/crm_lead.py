# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string="Project",
    )
    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='lead_id',
        string="Timesheet",
    )
