# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def write(self, vals):
        res = super().write(vals)
        sale_line_id = vals.get('sale_line_id', None)
        if sale_line_id is None:
            return res
        # Avoid rewrite so_line if billable_type is employee_rate
        self.filtered(
            lambda t: t.billable_type == 'task_rate'
        ).sudo().mapped('timesheet_ids').filtered(lambda l: (
            not l.timesheet_invoice_id and l.so_line.id != sale_line_id
        )).write({
            'so_line': sale_line_id,
        })
        return res
