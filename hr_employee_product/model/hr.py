# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp import SUPERUSER_ID


class HrAnalyticTimesheet(orm.Model):

    _inherit = 'hr.analytic.timesheet'

    def on_change_unit_amount(self, cr, uid, id, prod_id, unit_amount,
                              company_id, unit=False, journal_id=False,
                              context=None):
        return super(HrAnalyticTimesheet, self).on_change_unit_amount(
            cr, SUPERUSER_ID, id, prod_id, unit_amount, company_id, unit=False,
            journal_id=False, context=context)

    def _getGeneralAccount(self, cr, uid, context=None):
        return super(HrAnalyticTimesheet, self)._getGeneralAccount(
            cr, SUPERUSER_ID, context=context)

    def _getEmployeeUnit(self, cr, uid, context=None):
        return super(HrAnalyticTimesheet, self)._getEmployeeUnit(
            cr, SUPERUSER_ID, context=context)

    def _getEmployeeProduct(self, cr, uid, context=None):
        return super(HrAnalyticTimesheet, self)._getEmployeeProduct(
            cr, SUPERUSER_ID, context=context)

    _defaults = {
        'product_uom_id': _getEmployeeUnit,
        'product_id': _getEmployeeProduct,
        'general_account_id': _getGeneralAccount,
    }
