# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#
##############################################################################
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv


class hr_timesheet_invoice_create(osv.osv_memory):
    _inherit = 'hr.timesheet.invoice.create'

    def do_create(self, cr, uid, ids, context=None):
        """ If the wizard is called from hr.analytic.timesheet (inherits account.analytic.line)
            We get the account.analytic.line ids and call the wizard with them """
        if context.get('active_model', False) == 'hr.analytic.timesheet':
            at_obj = self.pool.get('hr.analytic.timesheet')
            at_ids = context.get('active_ids', False)
            aal_ids = [at.line_id.id for at in at_obj.browse(cr, uid, at_ids, context)]
            context['active_ids'] = aal_ids
        return super(hr_timesheet_invoice_create, self).do_create(cr, uid, ids, context)

hr_timesheet_invoice_create()
