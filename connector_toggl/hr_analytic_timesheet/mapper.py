# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import hashlib
import re

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.addons.connector.unit.mapper import mapping, ImportMapper
from openerp.addons.connector.exception \
    import MappingError, InvalidDataError, IDMissingInBackend

from .. import toggl


_logger = logging.getLogger(__name__)


@toggl
class HrAnalyticTimesheetImportMapper(ImportMapper):
    _model_name = 'toggl.hr.analytic.timesheet'

    @mapping
    def user(self, record):
        """ user and related product """
        key = re.sub(r'\W+', '', record['user'].lower())
        userinfo = self.options.usertable.get(key, None)
        if userinfo:
            user_id = userinfo['user_id']
            employee = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1)
            if not employee:
                raise UserError(_("User %s does not have a related employee!"
                    % (str(user_id))))
            if not employee.product_id:
                raise UserError(_("Employee %s does not have a timesheet product defined!"
                    % (employee.name)))
            return {
                'user_id': user_id,
                'product_id': employee.product_id.id
            }
        else:
            raise MappingError

    @mapping
    def duration(self, record):
        """ Duration not in milliseconds but 15-minute-rounded hours """
        return {'unit_amount': round(record['duration'] / 900000.0) / 4.0}

    @mapping
    def date(self, record):
        """ Dates to Odoo """
        return {'date': fields.Date.to_string(record['date'])}

    @mapping
    def product_constants(self, record):
        return {
            'resource_type': 'material',
            'backend_id': self.backend_record.id,
            'active': True,
        }

    @mapping
    def name_of_line(self, record):
        return {
            'name': record.get('description', _('Unknown')),
        }

    # add analytic account name
    @mapping
    def analytic_account(self, record):
        account_obj = self.env['account.analytic.account']
        partner_obj = self.env['res.partner']
        user = self.env['res.users'].browse(self.env.uid)
        company_name = user.company_id.name
        partner_name = record['client'] or company_name
        partners = partner_obj.search([
            ('name', '=', partner_name),
        ])
        if not partners:
            raise UserError(_("Unable to find partner with name '%s' \n. ") %
                (partner_name,))
        project_name = record['project'] or company_name
        account = account_obj.search([
            ('partner_id', 'in', partners.ids),
            ('name', '=', project_name),
            ('state', '!=', 'close')
        ])
        if not account:
            raise UserError(_("Unable to find project named %s "
                "for partner %s" % (project_name, partner_name)))
        elif len(account) > 1:
            raise UserError(_("There is more than one project named %s "
                "for partner %s" % (project_name, partner_name)))
        return {
            'account_id': account.id
        }

    # add default to_invoice as 100%
    @mapping
    def to_invoice(self, record):
        return {'to_invoice': self.env.ref('hr_timesheet_invoice.timesheet_invoice_factor1').id}

