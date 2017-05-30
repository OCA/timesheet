# -*- coding: utf-8 -*-

import openerp.addons.connector.backend as backend
toggl = backend.Backend('toggl', version='1.0')

from openerp.addons.connector.connector import ConnectorEnvironment
def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.env['toggl.backend'].browse(backend_id)
    return ConnectorEnvironment(backend_record, session, model_name)

from . import models
from . import hr_analytic_timesheet
