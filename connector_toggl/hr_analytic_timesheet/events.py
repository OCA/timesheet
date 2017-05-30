# -*- coding: utf-8 -*-
# © 2016 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp.addons.connector.event import Event

from importer_batch import import_from_toggl

_logger = logging.getLogger(__name__)

on_import_from_toggl = Event()

@on_import_from_toggl
def run_import_timesheets(session, model_name, filters=None):
    """ Run Import Timesheets from toggl"""
    # import_from_toggl.delay(
    #     session, model_name, context=dict(session.context))
    import_from_toggl(session, model_name, filters,
        context=dict(session.context))