# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class HrTimesheetReportWizard(models.TransientModel):
    _name = 'hr.timesheet.report.wizard'
    _description = 'HR Timesheet Report Wizard'

    line_ids = fields.Many2many(
        string='Account Analytics Lines',
        comodel_name='account.analytic.line',
    )
    has_line_ids = fields.Boolean(
        string='Has lines (technical)',
        compute='_compute_has_line_ids',
    )
    date_from = fields.Date(
        string='Start Date',
    )
    date_to = fields.Date(
        string='End Date',
    )
    project_ids = fields.Many2many(
        string='Projects',
        comodel_name='project.project',
    )
    task_ids = fields.Many2many(
        string='Tasks',
        comodel_name='project.task',
    )
    employee_ids = fields.Many2many(
        string='Employees',
        comodel_name='hr.employee',
    )
    employee_category_ids = fields.Many2many(
        string='Employee Tags',
        comodel_name='hr.employee.category',
    )
    department_ids = fields.Many2many(
        string='Departments',
        comodel_name='hr.department',
    )
    grouping_field_ids = fields.One2many(
        string='Grouping Fields',
        comodel_name='hr.timesheet.report.wizard.field.grouping',
        inverse_name='wizard_id',
        default=lambda self: self._default_grouping_field_ids(),
    )
    entry_field_ids = fields.One2many(
        string='Details Fields',
        comodel_name='hr.timesheet.report.wizard.field.details',
        inverse_name='wizard_id',
        default=lambda self: self._default_entry_field_ids(),
    )
    time_format = fields.Selection(
        string='Time format',
        selection=lambda self: self._selection_time_format(),
        required=True,
        default=lambda self: self._selection_time_format()[0][0],
    )

    @api.model
    def create(self, vals):
        if 'grouping_field_ids' not in vals:
            # In order to avoid empty set being replaced with default value:
            vals.update({
                'grouping_field_ids': [(5, False, False)],
            })
        if 'entry_field_ids' not in vals:
            raise UserError(_('At least one Details field must be specified!'))
        return super().create(vals)

    @api.model
    def _default_grouping_field_ids(self):
        return list(map(
            lambda values: (0, False, values),
            self._get_default_grouping_fields()
        ))

    @api.model
    def _get_default_grouping_fields(self):
        return [
            {
                'sequence': 10,
                'field_name': 'project_id',
            },
            {
                'sequence': 20,
                'field_name': 'task_id',
            },
            {
                'sequence': 30,
                'field_name': 'employee_id',
            },
        ]

    @api.model
    def _default_entry_field_ids(self):
        return list(map(
            lambda values: (0, False, values),
            self._get_default_entry_fields()
        ))

    @api.model
    def _get_default_entry_fields(self):
        return [
            {
                'sequence': 10,
                'field_name': 'date',
            },
            {
                'sequence': 20,
                'field_name': 'name',
            },
        ]

    @api.model
    def _selection_time_format(self):
        Report = self.env['hr.timesheet.report']
        return Report._selection_time_format()

    @api.constrains('entry_field_ids')
    def _check_entry_field_ids(self):
        for wizard in self:
            if len(wizard.entry_field_ids) < 1:
                raise ValidationError(_(
                    'At least one field must be listed in Details Fields'
                ))

    @api.multi
    @api.depends('line_ids')
    def _compute_has_line_ids(self):
        for wizard in self:
            wizard.has_line_ids = len(wizard.line_ids) > 0

    @api.multi
    def action_export_html(self):
        self.ensure_one()

        action = self._generate_report('qweb-html')
        if not self.has_line_ids:
            action.update({
                'target': 'main',
            })

        return action

    @api.multi
    def action_export_pdf(self):
        self.ensure_one()

        return self._generate_report('qweb-pdf')

    @api.multi
    def action_export_xlsx(self):
        self.ensure_one()

        return self._generate_report('xlsx')

    @api.multi
    def _generate_report(self, report_type):
        self.ensure_one()

        report = self.env['hr.timesheet.report'].create(
            self._collect_report_values()
        )

        return report.get_action(report_type)

    @api.multi
    def _collect_report_values(self):
        self.ensure_one()

        return {
            'line_ids': [(6, False, self.line_ids.ids)],
            'date_from': self.date_from,
            'date_to': self.date_to,
            'project_ids': [(6, False, self.project_ids.ids)],
            'task_ids': [(6, False, self.task_ids.ids)],
            'employee_ids': [(6, False, self.employee_ids.ids)],
            'employee_category_ids': [
                (6, False, self.employee_category_ids.ids)
            ],
            'department_ids': [(6, False, self.department_ids.ids)],
            'groupby_field_ids': list(map(
                lambda x: (0, False, x._collect_report_values()),
                self.grouping_field_ids
            )),
            'entry_field_ids': list(map(
                lambda x: (0, False, x._collect_report_values()),
                self.entry_field_ids
            )),
            'time_format': self.time_format,
        }


class HrTimesheetReportWizardField(models.AbstractModel):
    _name = 'hr.timesheet.report.wizard.field'
    _description = 'HR Timesheet Report Wizard field'
    _order = 'sequence, id'

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='hr.timesheet.report.wizard',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
        default=10,
    )
    field_name = fields.Selection(
        string='Field',
        selection='_selection_field_name',
        required=True,
    )
    field_title = fields.Char(
        string='Title',
        compute='_compute_field_title',
    )
    field_type = fields.Char(
        string='Type',
        compute='_compute_field_type',
    )

    @api.model
    def _selection_field_name(self):
        fields = self.env['account.analytic.line'].fields_get().items()
        return [
            (f, d.get('string')) for f, d in fields if self._field_selectable(
                f, d)
        ]

    @api.model
    def _field_selectable(self, field, definition):
        return True

    @api.multi
    @api.depends('field_name')
    def _compute_field_title(self):
        fields = self.env['account.analytic.line'].fields_get()
        for field in self:
            field.field_title = fields[field.field_name]['string']

    @api.multi
    @api.depends('field_name')
    def _compute_field_type(self):
        fields = self.env['account.analytic.line'].fields_get()
        for field in self:
            field.field_type = fields[field.field_name]['type']

    @api.multi
    def _collect_report_values(self):
        self.ensure_one()

        return {
            'sequence': self.sequence,
            'field_name': self.field_name,
            'field_title': self.field_title,
            'field_type': self.field_type,
            'aggregation': (
                'day' if self.field_type in ['datetime', 'date'] else None
            ),
        }


class HrTimesheetReportWizardGroupingField(models.TransientModel):
    _name = 'hr.timesheet.report.wizard.field.grouping'
    _description = 'HR Timesheet Report Wizard field (grouping)'
    _inherit = 'hr.timesheet.report.wizard.field'


class HrTimesheetReportWizardDetailsField(models.TransientModel):
    _name = 'hr.timesheet.report.wizard.field.details'
    _description = 'HR Timesheet Report Wizard field (details)'
    _inherit = 'hr.timesheet.report.wizard.field'
