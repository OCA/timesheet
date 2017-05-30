# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import models, fields, api, _
from openerp.addons.connector.session import ConnectorSession

_logger = logging.getLogger(__name__)


class TogglHrAnalyticTimesheet(models.Model):
    """ Add openerp_id on binding record """
    _name = 'toggl.hr.analytic.timesheet'
    _inherit = 'toggl.binding'
    _inherits = {'hr.analytic.timesheet': 'openerp_id'}
    _description = 'Toggl Timesheet Line'

    openerp_id = fields.Many2one(comodel_name='hr.analytic.timesheet',
        string='Timesheet line', required=True, ondelete='cascade')


class HrAnalyticTimesheet(models.Model):
    """ Add relation to toggl records on timesheet line """
    _inherit = 'hr.analytic.timesheet'

    toggl_bind_ids = fields.One2many(
        comodel_name='toggl.hr.analytic.timesheet',
        inverse_name='openerp_id',
        string='Toggl Bindings',
    )


class HrTimesheet(models.Model):
    """ Add import button on timesheet """
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.multi
    def import_from_toggl(self):
        """ Import From Toggl """
        self.ensure_one()
        from events import on_import_from_toggl
        session = ConnectorSession(self.env.cr, self.env.uid,
            context=self.env.context)

        model_name = 'toggl.hr.analytic.timesheet'
        filters = {
            'date_from': fields.Date.from_string(self.date_from),
            'date_to': fields.Date.from_string(self.date_to),
            'name': self.employee_id.name
        }
        if on_import_from_toggl.has_consumer_for(session, model_name):
            on_import_from_toggl.fire(session, model_name, filters)
