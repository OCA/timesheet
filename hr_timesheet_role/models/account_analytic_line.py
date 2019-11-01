# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    role_id = fields.Many2one(
        comodel_name='project.role',
        string='Role',
        required=False,
        domain=lambda self: self._domain_role_id(),
    )
    is_role_required = fields.Boolean(
        related='project_id.is_timesheet_role_required',
    )
    limit_role_to_assignments = fields.Boolean(
        related='project_id.limit_role_to_assignments',
    )

    @api.multi
    @api.constrains('project_id', 'employee_id', 'role_id')
    def _check_role_id(self):
        for line in self:
            if line.limit_role_to_assignments and not line._is_role_valid():
                raise ValidationError(
                    _(
                        '%s can not act as %s on %s project'
                    ) % (
                        line.employee_id.name,
                        line.role_id.name or _('unassigned'),
                        line.project_id.name,
                    )
                )

    @api.onchange('project_id', 'employee_id')
    def _onchange_project_or_employee(self):
        self._validate_role()
        return {
            'domain': {
                'role_id': self._domain_role_id(),
            },
        }

    @api.multi
    def _validate_role(self):
        for line in self:
            if line.project_id and line.employee_id:
                if not line._is_role_valid():
                    line.role_id = False

    @api.multi
    def _is_role_valid(self):
        self.ensure_one()

        user_id = self.employee_id.user_id or self.env['res.users'].browse(
            self._default_user()
        )

        # If there's no role set, is_role_required defines if that's ok
        if not self.role_id:
            return not self.is_role_required

        # If nothing is set, any role would be invalid since there's no
        # way way to validate it.
        if not self.project_id or not user_id:  # pragma: no cover
            return False

        role_ids = self.env['project.role'].get_available_roles(
            user_id,
            self.project_id
        )
        return self.role_id in role_ids

    def _domain_role_id(self):
        user_id = self.employee_id.user_id or self.env['res.users'].browse(
            self._default_user()
        )

        if not self.project_id:
            role_ids = self.env['project.role'].search([
                ('company_id', 'in', [False, user_id.company_id.id]),
            ])
        else:
            role_ids = self.env['project.role'].get_available_roles(
                user_id,
                self.project_id
            )
        return [('id', 'in', role_ids.ids)]
