# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
import logging
from openerp.addons.connector.connector import ConnectorEnvironment

class TogglBinding(models.AbstractModel):
    """ Abstract Model for the Bindings. All the models used as bindings 
    between Toggl and OpenERP should ``_inherit`` it. """
    _name = 'toggl.binding'
    _inherit = 'external.binding'
    _description = 'Toggl Binding (abstract)'

    # openerp_id = openerp-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='toggl.backend',
        string='Toggl Backend',
        required=True,
        ondelete='restrict',
    )
    toggl_id = fields.Char(size=20, string='ID in Toggl')

    _sql_constraints = [
        ('toggl_uniq', 'unique(backend_id, toggl_id)',
         'A binding already exists with the same Toggl ID.'),
    ]

def get_environment(session, model_name):
    """ Create an environment to work with. """
    backend_record = session.env['toggl.backend'].sudo().search([], limit=1)
    env = ConnectorEnvironment(backend_record, session, model_name)
    # lang = backend_record.default_lang_id # backend_record missing default_lang_id
    # lang = session.context.get('lang')
    # lang_code = lang.code if lang else 'nl_NL'
    lang_code = 'en_US'
    if lang_code == session.context.get('lang'):
        return env
    else:
        with env.session.change_context(lang=lang_code):
            return env
