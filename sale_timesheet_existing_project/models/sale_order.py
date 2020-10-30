# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    visible_project = fields.Boolean(
        string='Display project',
        compute='_compute_visible_project',
    )
    project_id = fields.Many2one(
        'project.project', 'Project',
        domain="[('billable_type', 'in', ('no', 'task_rate')),"
               " ('analytic_account_id', '!=', False),"
               " ('company_id', '=', company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                'sale': [('readonly', False)], 'done': [('readonly', False)]},
        help='Select a non billable project on which tasks can be created.')

    @api.depends('order_line.product_id.service_tracking')
    def _compute_visible_project(self):
        """ Users should be able to select a project_id on the SO if at least
        one SO line has a product with its service tracking configured as
        'task_in_project' """
        for order in self:
            order.visible_project = any(
                service_tracking == 'task_in_project'
                for service_tracking
                in order.order_line.mapped('product_id.service_tracking')
            )

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            if order.state == 'sale' and order.visible_project and not \
                    order.project_id and any(order.mapped('order_line.project_id')):
                raise UserError(_('Missing project in sale order, but almost one '
                                  'line of the order have a project: assign one of '
                                  'these projects to the sale order!'))
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_service_generation(self):
        """Handle task creation with sales order's project."""
        so_lines = self.filtered(lambda sol: (
            sol.is_service and
            sol.product_id.service_tracking == 'task_in_project'))
        map_so_project = {}
        for so_line in so_lines:
            if so_line.order_id.project_id:
                project = so_line.order_id.project_id
            else:
                order = so_line.order_id
                if map_so_project.get(order):
                    project = map_so_project[order]
                else:
                    project = so_line._timesheet_create_project()
                    map_so_project[order] = project
            so_line.project_id = project
            so_line._timesheet_create_task(project=project)
        return super()._timesheet_service_generation()
