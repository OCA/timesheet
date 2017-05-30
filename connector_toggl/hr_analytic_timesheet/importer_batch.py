# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re
import os
from openerp import models, fields, api, _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.exception \
    import MappingError, InvalidDataError, IDMissingInBackend
from openerp.addons.connector_toggl.models.connector import get_environment
import json

from .. import toggl
from ..unit.importer import TogglBatchImporter
from .mapper import HrAnalyticTimesheetImportMapper
from datetime import datetime, timedelta
from openerp.addons.connector.connector import ConnectorEnvironment

_logger = logging.getLogger(__name__)


@toggl
class HrAnalyticTimesheetBatchImporter(TogglBatchImporter):
    """ Import the Toggl timesheet lines. """

    _model_name = ['toggl.hr.analytic.timesheet']

    def _fill_user_translation_table(self):
        userinfo = {}
        users = self.env['hr.employee'].search([('user_id', '!=', False)])
        for user in users:
            key = re.sub(r'\W+', '', user.user_id.name.lower())
            userinfo[key] = {
                'name': user.user_id.name,
                'user_id': user.user_id.id,
            }
        self._user_translation_table = userinfo

    @property
    def mapper(self):
        return self.unit_for(HrAnalyticTimesheetImportMapper)

    def run(self, filters=None, from_file=None):
        """ Run the synchronization """
        self._fill_user_translation_table()

        date_from = filters.get('date_from', None)
        date_to = filters.get('date_to', None)
        employee_name = filters.get('name', None)
        if not (date_from and date_to and employee_name):
            raise UserError('No date and/or employee selected')
        if from_file:
            # Get the new records from a file
            with open(from_file) as data_file:
                resultlines = json.load(data_file)
        else:
            # Get the new records from Toggl
            resultlines = self.backend_adapter.search_read(filters=filters)
        _logger.info("%d timesheet lines selected for sync", len(resultlines))

        # Aggregate the lines
        new_records = self.backend_adapter.aggregate(resultlines)

        # Delete all the current Toggl records we know from this period
        if date_from and date_to:
            odoo_date_from = fields.Date.to_string(date_from)
            odoo_date_to = fields.Date.to_string(date_to)
            records = self.model.search([
                ('date', '>=', odoo_date_from),
                ('date', '<=', odoo_date_to),
                ('user_id.name', '=', employee_name)
            ])
            real_records = records.mapped('openerp_id')
            records.unlink()
            real_records.unlink()

        # Loop and import records
        for record in new_records:
            self._import_record(record)

    def _import_record(self, values):
        # save toggl id on object
        self.toggl_id = values['id']

        # Keep a lock on this import until the transaction is committed
        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.model._name,
            self.toggl_id,
        )
        self.advisory_lock_or_retry(lock_name)

        # gets the current Odoo record, or None if there is no Odoo record yet
        binding = self.binder.to_openerp(self.toggl_id, browse=True)
        # Accessing relations of the binding locks the system, so requery the record
        if binding:
            origmodel = self.binder.unwrap_model()
            requeried = self.env[origmodel].browse(binding.openerp_id.id)

        try:
            # map toggl record to an odoo dictionary
            map_record = self.mapper.map_record(values)
            if binding:
                # FOR UPDATE
                record = map_record.values(
                    usertable=self._user_translation_table
                ) 
            else:
                # FOR CREATE
                record = map_record.values(
                    usertable=self._user_translation_table,
                    for_create=True
                )

        except MappingError:
            _logger.error('Cannot map data for this timesheet line, skipping.')
            return None

        except InvalidDataError:
            _logger.error('Invalid data for this timesheet line, skipping.')
            return None
            
        # update or create the odoo record
        if binding:
            # update the odoo record
            binding.with_context(connector_no_export=True).write(record)
            # update 'active' for the product template record
            _logger.info('%d updated from Toggl %s', binding, self.toggl_id)
        else:
            # create the odoo record
            binding = self.model.with_context(connector_no_export=True) \
                .create(record)
            _logger.info('%d (%s) created from Toggl %s', binding,
                record['name'], self.toggl_id)

        # 'bind' the records by updating the 'toggl.*' record
        # and updating it with the most recent sync date
        self.binder.bind(self.toggl_id, binding)

@job
def import_from_toggl(session, model_name, filters, context=None):
    """ Import from Toggl """
    env = get_environment(session, model_name)
    importer = env.get_connector_unit(HrAnalyticTimesheetBatchImporter)

    # do a full sync
    importer.run(filters=filters, from_file=None)

