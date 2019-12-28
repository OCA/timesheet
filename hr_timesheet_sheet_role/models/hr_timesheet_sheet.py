# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    add_line_role_id = fields.Many2one(
        comodel_name='project.role',
        string='Select Role',
        domain=lambda self: self._domain_add_line_role_id(),
        help=(
            'If selected, the associated role is added '
            'to the timesheet sheet when clicked the button.'
        ),
        states={
            'draft': [('readonly', False)],
        },
    )
    add_line_limit_role_to_assignments = fields.Boolean(
        related='add_line_project_id.limit_role_to_assignments',
    )

    @api.multi
    @api.constrains('company_id', 'add_line_role_id')
    def _check_company_id_add_line_role_id(self):
        for sheet in self:
            if sheet.company_id and sheet.add_line_role_id.company_id and \
                    sheet.company_id != sheet.add_line_role_id.company_id:
                raise ValidationError(_(
                    'The Company in the Timesheet Sheet and in the Role must'
                    ' be the same.'
                ))

    @api.onchange('add_line_project_id')
    def onchange_add_project_id(self):
        result = super().onchange_add_project_id()

        result['domain'].update({
            'add_line_role_id': self._domain_add_line_role_id(),
        })

        return result

    def _domain_add_line_role_id(self):
        if not self.add_line_project_id:
            role_ids = self.env['project.role'].search([
                ('company_id', 'in', [False, self.user_id.company_id.id]),
            ])
        else:
            role_ids = self.env['project.role'].get_available_roles(
                self.user_id,
                self.add_line_project_id
            )
        return [('id', 'in', role_ids.ids)]

    @api.model
    def _matrix_key_attributes(self):
        res = super()._matrix_key_attributes()
        res.append('role_id')
        return res

    @api.model
    def _get_matrix_key_values_for_line(self, aal):
        res = super()._get_matrix_key_values_for_line(aal)
        res.update({
            'role_id': aal.role_id,
        })
        return res

    @api.multi
    def _get_default_sheet_line(self, matrix, key):
        res = super()._get_default_sheet_line(matrix, key)
        res.update({
            'role_id': key.role_id.id,
        })
        return res

    @api.multi
    def _get_new_line_unique_id(self):
        res = super()._get_new_line_unique_id()
        res.update({
            'role_id': self.add_line_role_id,
        })
        return res

    @api.multi
    def _get_line_name(self, project_id, task_id=None, role_id=None, **kwargs):
        res = super()._get_line_name(
            project_id=project_id,
            task_id=task_id,
            role_id=role_id,
            **kwargs
        )
        if role_id:
            res += ' - %s' % (role_id.name_get()[0][1])
        return res

    @api.multi
    def reset_add_line(self):
        super().reset_add_line()
        self.write({
            'add_line_role_id': False,
        })

    @api.model
    def _prepare_empty_analytic_line(self):
        res = super()._prepare_empty_analytic_line()
        res.update({
            'role_id': self.add_line_role_id.id,
        })
        return res

    @api.model
    def _prepare_new_line(self, line):
        res = super()._prepare_new_line(line)
        res.update({
            'role_id': line.role_id.id,
        })
        return res

    @api.multi
    def _is_add_line(self, row):
        return super()._is_add_line(row) \
            and self.add_line_role_id == row.role_id

    @api.model
    def _is_line_of_row(self, aal, row):
        return super()._is_line_of_row(aal, row) \
            and aal.role_id.id == row.role_id.id

    @api.multi
    def _is_compatible_new_line(self, line_a, line_b):
        return super()._is_compatible_new_line(line_a, line_b) \
            and line_a.role_id.id == line_b.role_id.id


class AbstractSheetLine(models.AbstractModel):
    _inherit = 'hr_timesheet.sheet.line.abstract'

    role_id = fields.Many2one(
        comodel_name='project.role',
        string='Role',
    )

    @api.multi
    def get_unique_id(self):
        res = super().get_unique_id()
        res.update({
            'role_id': self.role_id,
        })
        return res


class SheetNewAnalyticLine(models.TransientModel):
    _inherit = 'hr_timesheet.sheet.new.analytic.line'

    @api.model
    def _is_similar_analytic_line(self, aal):
        return super()._is_similar_analytic_line(aal) \
            and aal.role_id.id == self.role_id.id
