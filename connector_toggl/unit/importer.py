# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import fields, _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Importer
from .. import toggl, get_environment

_logger = logging.getLogger(__name__)


class TogglBatchImporter(Importer):
    """ Base batch importer for Toggl """

    def run(self, filters=None, from_file=None):
        pass


@job(default_channel='root')
def import_batch(session, model_name, backend_id, filters=None,
        from_file=None, next_time=None):
    """ Prepare a batch import of records from Toggl """
    env = get_environment(session, model_name, backend_id)
    batchimporter = env.get_connector_unit(TogglBatchImporter)
    batchimporter.run(filters=filters, from_file=from_file)

    # when job successful, update next_time
    Backend = session.env['toggl.backend']
    for backend in Backend.browse(backend_id):
        backend.write({'import_from_date': next_time})



