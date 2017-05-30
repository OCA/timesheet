# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
from datetime import datetime
from openerp import models, fields, api, _, tools
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import ConnectorUnit
from ..unit.importer import import_batch

_logger = logging.getLogger(__name__)


class TogglBackend(models.Model):
    _name = 'toggl.backend'
    _description = 'Toggl Backend'
    _inherit = 'connector.backend'
    _backend_type = 'toggl'

    version = fields.Selection(selection=[('1.0', '1.0+')])
    api_url = fields.Char(
        string="Toggl API URL",
        required=True,
        default="https://toggl.com/reports/api/v2/details",
        help="URL of Toggl API"
    )
    api_key = fields.Char(
        string='Toggl API key',
        required=True,
        help="API key given by Toggl",
    )
    workspace_id = fields.Char(
        string='Toggl workspace ID',
        required=True,
        help="ID of workspace to import from. Can be found by clicking "
             "your workspace in Toggl and reading the id from the URL.",
    )
    import_from_date = fields.Datetime(
        string='Import from date',
    )
    hr_analytic_timesheet_binding_ids = fields.One2many(
        comodel_name='toggl.hr.analytic.timesheet',
        inverse_name='backend_id',
        string='Toggl timesheet lines',
        readonly=True,
    )

    @api.multi
    def import_records(self):
        """ Import from date """

        # ensure only one backend selected
        self.ensure_one()

        # start connector session
        session = ConnectorSession(
            self.env.cr,
            self.env.uid,
            context=self.env.context
        )

        # find the date range to import
        model = 'toggl.hr.analytic.timesheet'
        from_date = self.import_from_date
        to_date = datetime.now()
        next_time = fields.Datetime.to_string(to_date)
        _logger.info('==== Starting Toggl sync from date %s ====', str(from_date))

        # For tests
        from_file = self.env.context.get('from_file', None)

        # no delay but import directly
        import_batch(
            session,
            model,
            self.id,
            filters={
                'from_date': from_date,
                'to_date': to_date
            },
            from_file=from_file,
            next_time=next_time
        )
