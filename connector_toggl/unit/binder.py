# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp
from openerp.addons.connector.connector import Binder
from .. import toggl


@toggl
class TogglModelBinder(Binder):
    """ Binding models are models called ``toggl.{normal_model}``. """
    _model_name = [
        'toggl.hr.analytic.timesheet',
    ]

    def to_openerp(self, external_id, unwrap=False, browse=False):
        """ Give the OpenERP ID for an external ID """
        bindings = self.model.with_context(active_test=False).search([
            ('toggl_id', '=', str(external_id)),
            ('backend_id', '=', self.backend_record.id)
        ])
        if not bindings:
            return self.model.browse() if browse else None
        assert len(bindings) == 1, "Several records found: %s" % (bindings,)
        if unwrap:
            return bindings.openerp_id if browse else bindings.openerp_id.id
        else:
            return bindings if browse else bindings.id

    def to_backend(self, record_id, wrap=False):
        """ Give the external ID for an OpenERP ID """
        record = self.model.browse()
        if isinstance(record_id, openerp.models.BaseModel):
            record_id.ensure_one()
            record = record_id
            record_id = record_id.id
        if wrap:
            binding = self.model.with_context(active_test=False).search([
                ('openerp_id', '=', record_id),
                ('backend_id', '=', self.backend_record.id),
            ])
            if binding:
                binding.ensure_one()
                return binding.toggl_id
            else:
                return None
        if not record:
            record = self.model.browse(record_id)
        assert record
        return record.toggl_id

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID
        update the last synchronization date. """
        # avoid to trigger the export when we modify the `toggl_id`
        now_fmt = openerp.fields.Datetime.now()
        if not isinstance(binding_id, openerp.models.BaseModel):
            binding_id = self.model.browse(binding_id)
        binding_id.with_context(connector_no_export=True).write({
            'toggl_id': str(external_id),
            'sync_date': now_fmt,
        })

    def unwrap_binding(self, binding_id, browse=False):
        """ For a binding record, gives the normal record. """
        if isinstance(binding_id, openerp.models.BaseModel):
            binding = binding_id
        else:
            binding = self.model.browse(binding_id)

        openerp_record = binding.openerp_id
        if browse:
            return openerp_record
        return openerp_record.id

    def unwrap_model(self):
        """ For a binding model, gives the name of the normal model. """
        try:
            column = self.model._fields['openerp_id']
        except KeyError:
            raise ValueError('Cannot unwrap model %s, because it has '
                             'no openerp_id field' % self.model._name)
        return column.comodel_name
