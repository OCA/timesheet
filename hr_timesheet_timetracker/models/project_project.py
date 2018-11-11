# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    timetracker_rounding_enabled = fields.Boolean(
        string='Apply Rounding',
        default=lambda self: self._default_timetracker_rounding_enabled(),
    )
    timetracker_started_at_rounding = fields.Selection(
        string='Started At rounding',
        selection='_selection_rounding',
        default=lambda self: self._default_timetracker_started_at_rounding(),
    )
    timetracker_stopped_at_rounding = fields.Selection(
        string='Stopped At rounding',
        selection='_selection_rounding',
        default=lambda self: self._default_timetracker_stopped_at_rounding(),
    )

    @api.model
    def _selection_rounding(self):
        return self.env['res.company']._selection_rounding()

    @api.model
    def _default_timetracker_rounding_enabled(self):
        company = self.env['res.company'].browse(
            self._context.get('company_id', self.env.user.company_id.id)
        )
        return company.timetracker_rounding_enabled

    @api.model
    def _default_timetracker_started_at_rounding(self):
        company = self.env['res.company'].browse(
            self._context.get('company_id', self.env.user.company_id.id)
        )
        return company.timetracker_started_at_rounding

    @api.model
    def _default_timetracker_stopped_at_rounding(self):
        company = self.env['res.company'].browse(
            self._context.get('company_id', self.env.user.company_id.id)
        )
        return company.timetracker_stopped_at_rounding
