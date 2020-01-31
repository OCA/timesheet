# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import ustr
from odoo.tools.safe_eval import safe_eval

import html
from functools import reduce
from xlsxwriter.utility import xl_rowcol_to_cell
import pytz
from datetime import datetime, time


class HrUtilizationReport(models.TransientModel):
    _name = 'hr.utilization.report'
    _description = 'HR Utilization Report'

    date_from = fields.Date(
        string='Start Date',
        required=True,
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
    )
    only_active_employees = fields.Boolean(
        string='Only Active Employees',
        default=True,
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
    groupby_field_ids = fields.One2many(
        string='Group-By Fields',
        comodel_name='hr.utilization.report.field.groupby',
        inverse_name='report_id',
    )
    entry_field_ids = fields.One2many(
        string='Entry Fields',
        comodel_name='hr.utilization.report.field.entry',
        inverse_name='report_id',
    )
    split_by_field_name = fields.Selection(
        string='Split-By Field',
        selection=lambda self: self._selection_split_by_field_name(),
    )
    utilization_format = fields.Selection(
        string='Utilization format',
        selection=lambda self: self._selection_utilization_format(),
        required=True,
    )
    time_format = fields.Selection(
        string='Time format',
        selection=lambda self: self._selection_time_format(),
        required=True,
    )
    split_by_field_title = fields.Char(
        string='Split-By Field Title',
        compute='_compute_split_by_field_title',
    )
    group_ids = fields.One2many(
        string='Groups',
        comodel_name='hr.utilization.report.group',
        inverse_name='report_id',
        compute='_compute_group_ids',
        store=True,
    )
    has_multientry_blocks = fields.Boolean(
        string='Has Multi-Entry Blocks',
        compute='_compute_has_multientry_blocks',
        store=True,
    )
    total_capacity = fields.Float(
        string='Total Capacity',
        compute='_compute_total_capacity',
        store=True,
    )
    total_unit_amount_a = fields.Float(
        string='Total Quantity (A)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_unit_amount_b = fields.Float(
        string='Total Quantity (B)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_utilization_a = fields.Float(
        string='Total Utilization (A)',
        compute='_compute_total_utilization',
        store=True,
    )
    total_utilization_b = fields.Float(
        string='Total Utilization (B)',
        compute='_compute_total_utilization',
        store=True,
    )

    @api.model
    def _selection_split_by_field_name(self):
        AccountAnalyticLine = self.env['account.analytic.line']

        def valid_field(f, d):
            return d.get('type') in [
                'boolean',
                'one2many',
                'many2one',
                'many2many',
            ]
        fields = AccountAnalyticLine.fields_get().items()

        return [(f, d.get('string')) for f, d in fields if valid_field(f, d)]

    @api.model
    def _selection_utilization_format(self):
        return [
            ('percentage', 'Percentage'),
            ('absolute', 'Absolute'),
        ]

    @api.model
    def _selection_time_format(self):
        return [
            ('hh_mm', 'Hours, minutes'),
            ('hh_mm_ss', 'Hours, minutes, seconds'),
            ('decimal', 'Decimal'),
        ]

    @api.model
    def _supported_report_types(self):
        return [
            'qweb-html',
            'qweb-pdf',
            'xlsx',
        ]

    @api.multi
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for analysis in self:
            if analysis.date_from > analysis.date_to:
                raise ValidationError(_(
                    'Date-To can not be earlier than Date-From'
                ))

    @api.multi
    @api.depends('split_by_field_name')
    def _compute_split_by_field_title(self):
        for analysis in self:
            if analysis.split_by_field_name:
                split_by_field_title = list(filter(
                    lambda x: x[0] == analysis.split_by_field_name,
                    analysis._selection_split_by_field_name()
                ))[0][1]
            else:
                split_by_field_title = None
            analysis.split_by_field_title = split_by_field_title

    @api.multi
    @api.depends(
        'only_active_employees',
        'employee_ids',
        'employee_category_ids',
        'department_ids',
        'groupby_field_ids',
    )
    def _compute_group_ids(self):
        HrEmployee = self.env['hr.employee']

        for report in self:
            group_ids = [(5, False, False)]

            if report.groupby_field_ids:
                grouped_employees = HrEmployee.read_group(
                    domain=report._get_employees_domain(),
                    fields=['id'],
                    groupby=report.groupby_field_ids.mapped('groupby'),
                    orderby=', '.join(
                        report.groupby_field_ids.mapped('field_name'),
                    ),
                    lazy=False,
                )

                for group_data in grouped_employees:
                    group_values = report._get_group_values(
                        group_data
                    )
                    if not group_values:
                        continue

                    group_values.update({
                        'sequence': len(group_ids),
                    })
                    group_ids.append((0, False, group_values))
            else:
                group_ids.append((0, False, {
                    'sequence': len(group_ids),
                    'name': None,
                    'scope': ustr(report._get_employees_domain()),
                }))

            report.group_ids = group_ids

    @api.multi
    def _get_group_values(self, grouped_lines):
        self.ensure_one()

        values = []
        for field in self.groupby_field_ids:
            value = grouped_lines.get(field.field_name, None)

            if not value:
                value = _('%s not set') % (field.field_title)
            else:
                value = value[1]

            values.append(value)

        return {
            'name': reduce(
                lambda l, r: _('{l} » {r}').format(l=l, r=r),
                values
            ),
            'scope': ustr(grouped_lines['__domain']),
        }

    @api.multi
    @api.depends('group_ids.has_multientry_blocks')
    def _compute_has_multientry_blocks(self):
        for report in self:
            report.has_multientry_blocks = any(
                report.group_ids.mapped('has_multientry_blocks')
            )

    @api.multi
    @api.depends('group_ids.total_capacity')
    def _compute_total_capacity(self):
        for report in self:
            report.total_capacity = sum(
                report.group_ids.mapped('total_capacity')
            )

    @api.multi
    @api.depends(
        'group_ids.total_unit_amount_a',
        'group_ids.total_unit_amount_b'
    )
    def _compute_total_unit_amount(self):
        for report in self:
            report.total_unit_amount_a = sum(
                report.group_ids.mapped('total_unit_amount_a')
            )
            report.total_unit_amount_b = sum(
                report.group_ids.mapped('total_unit_amount_b')
            )

    @api.multi
    @api.depends(
        'total_unit_amount_a',
        'total_unit_amount_b',
        'total_capacity'
    )
    def _compute_total_utilization(self):
        for report in self:
            if report.total_capacity != 0.0:
                total_utilization_a = (
                    report.total_unit_amount_a / report.total_capacity
                )
                total_utilization_b = (
                    report.total_unit_amount_b / report.total_capacity
                )
            else:
                total_utilization_a = float('+inf')
                total_utilization_b = float('+inf')
            report.total_utilization_a = total_utilization_a
            report.total_utilization_b = total_utilization_b

    @api.multi
    def _get_employees_domain(self):
        self.ensure_one()

        query = []

        if self.only_active_employees:
            query.append(('active', '=', True))
        employee_ids = (
            self.employee_ids
            | self.employee_category_ids.mapped('employee_ids')
        )
        if employee_ids:
            query.append(('id', 'in', employee_ids.ids))
        if self.department_ids:
            query.append(('department_id', 'in', self.department_ids.ids))

        return query

    @api.multi
    def get_action(self, report_type='qweb-html'):
        self.ensure_one()

        if report_type not in self._supported_report_types():
            raise UserError(_(
                '"%s" report type is not supported' % (
                    report_type
                )
            ))

        report_name = 'hr_utilization_report.report'

        action = self.env['ir.actions.report'].search([
            ('model', '=', self._name),
            ('report_name', '=', report_name),
            ('report_type', '=', report_type),
        ], limit=1)
        if not action:
            raise UserError(_(
                '"%s" report with "%s" type not found' % (
                    report_name,
                    report_type
                )
            ))

        context = dict(self.env.context)
        return action.with_context(context).report_action(self)


class HrUtilizationReportAbstractField(models.AbstractModel):
    _name = 'hr.utilization.report.field'
    _description = 'HR Utilization Report field'
    _order = 'sequence, id'

    report_id = fields.Many2one(
        string='Report',
        comodel_name='hr.utilization.report',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    field_name = fields.Char(
        string='Field name',
        required=True,
    )
    field_title = fields.Char(
        string='Field title',
        required=True,
    )
    field_type = fields.Char(
        string='Field type',
        required=True,
    )
    aggregation = fields.Char(
        string='Aggregation',
    )
    groupby = fields.Char(
        string='Group-by expression',
        compute='_compute_groupby',
    )

    _sql_constraints = [
        (
            'field_name_uniq',
            'UNIQUE(report_id, field_name)',
            'Field can be reported only once!'
        ),
    ]

    @api.depends('field_name', 'aggregation')
    @api.multi
    def _compute_groupby(self):
        for field in self:
            if field.aggregation:
                field.groupby = '%s:%s' % (field.field_name, field.aggregation)
            else:
                field.groupby = field.field_name


class HrUtilizationReportGroupByField(models.TransientModel):
    _name = 'hr.utilization.report.field.groupby'
    _description = 'HR Utilization Report field (groupby)'
    _inherit = 'hr.utilization.report.field'


class HrUtilizationReportEntryField(models.TransientModel):
    _name = 'hr.utilization.report.field.entry'
    _description = 'HR Utilization Report field (entry)'
    _inherit = 'hr.utilization.report.field'

    cell_classes = fields.Char(
        string='Cell classes',
        compute='_compute_cell_classes',
    )

    @api.multi
    @api.depends('field_type')
    def _compute_cell_classes(self):
        for field in self:
            field.cell_classes = ' '.join(
                field._get_cell_classes(field.field_type)
            )

    @api.multi
    def _get_cell_classes(self, field_type):
        self.ensure_one()

        return [] if field_type == 'char' else ['text-nowrap']


class HrUtilizationReportGroup(models.TransientModel):
    _name = 'hr.utilization.report.group'
    _description = 'HR Utilization Report group'
    _order = 'sequence, id'

    report_id = fields.Many2one(
        string='Report',
        comodel_name='hr.utilization.report',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    scope = fields.Char(
        string='Scope',
        required=True,
    )
    name = fields.Char()
    block_ids = fields.One2many(
        string='Blocks',
        comodel_name='hr.utilization.report.block',
        inverse_name='group_id',
        compute='_compute_block_ids',
        store=True,
    )
    has_multientry_blocks = fields.Boolean(
        string='Has Multi-Entry Blocks',
        compute='_compute_has_multientry_blocks',
        store=True,
    )
    total_capacity = fields.Float(
        string='Total Capacity',
        compute='_compute_total_capacity',
        store=True,
    )
    total_unit_amount_a = fields.Float(
        string='Total Quantity (A)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_unit_amount_b = fields.Float(
        string='Total Quantity (B)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_utilization_a = fields.Float(
        string='Total Utilization (A)',
        compute='_compute_total_utilization',
        store=True,
    )
    total_utilization_b = fields.Float(
        string='Total Utilization (B)',
        compute='_compute_total_utilization',
        store=True,
    )

    @api.multi
    @api.depends('scope')
    def _compute_block_ids(self):
        HrEmployee = self.env['hr.employee']

        for group in self:
            employee_ids = HrEmployee.search(
                safe_eval(group.scope)
            )

            block_ids = [(5, False, False)]
            for employee_id in employee_ids:
                block_ids.append((0, False, {
                    'sequence': len(block_ids),
                    'employee_id': employee_id.id,
                }))
            group.block_ids = block_ids

    @api.multi
    @api.depends('block_ids.is_multientry')
    def _compute_has_multientry_blocks(self):
        for group in self:
            group.has_multientry_blocks = any(
                group.block_ids.mapped('is_multientry')
            )

    @api.multi
    @api.depends('block_ids.capacity')
    def _compute_total_capacity(self):
        for group in self:
            group.total_capacity = sum(
                group.block_ids.mapped('capacity')
            )

    @api.multi
    @api.depends(
        'block_ids.total_unit_amount_a',
        'block_ids.total_unit_amount_b'
    )
    def _compute_total_unit_amount(self):
        for group in self:
            group.total_unit_amount_a = sum(
                group.block_ids.mapped('total_unit_amount_a')
            )
            group.total_unit_amount_b = sum(
                group.block_ids.mapped('total_unit_amount_b')
            )

    @api.multi
    @api.depends(
        'total_unit_amount_a',
        'total_unit_amount_b',
        'total_capacity'
    )
    def _compute_total_utilization(self):
        for group in self:
            if group.total_capacity != 0.0:
                total_utilization_a = (
                    group.total_unit_amount_a / group.total_capacity
                )
                total_utilization_b = (
                    group.total_unit_amount_b / group.total_capacity
                )
            else:
                total_utilization_a = float('+inf')
                total_utilization_b = float('+inf')
            group.total_utilization_a = total_utilization_a
            group.total_utilization_b = total_utilization_b


class HrUtilizationReportBlock(models.TransientModel):
    _name = 'hr.utilization.report.block'
    _description = 'HR Utilization Report block'
    _order = 'sequence, id'

    group_id = fields.Many2one(
        string='Group',
        comodel_name='hr.utilization.report.group',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        required=True,
    )
    entry_ids = fields.One2many(
        string='Entries',
        comodel_name='hr.utilization.report.entry',
        inverse_name='block_id',
        compute='_compute_entry_ids',
        store=True,
    )
    is_multientry = fields.Boolean(
        string='Is Multi-Entry',
        compute='_compute_is_multientry',
        store=True,
    )
    capacity = fields.Float(
        string='Capacity',
        compute='_compute_capacity',
        store=True,
    )
    total_unit_amount_a = fields.Float(
        string='Total Quantity (A)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_unit_amount_b = fields.Float(
        string='Total Quantity (B)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_utilization_a = fields.Float(
        string='Total Utilization (A)',
        compute='_compute_total_utilization',
        store=True,
    )
    total_utilization_b = fields.Float(
        string='Total Utilization (B)',
        compute='_compute_total_utilization',
        store=True,
    )

    @api.multi
    @api.depends(
        'group_id',
        'employee_id'
    )
    def _compute_entry_ids(self):
        AccountAnalyticLine = self.env['account.analytic.line']

        for block in self:
            entry_field_ids = block.group_id.report_id.entry_field_ids

            grouped_lines = AccountAnalyticLine.read_group(
                domain=block._get_entries_domain(),
                fields=['id'],
                groupby=entry_field_ids.mapped('groupby'),
                orderby=', '.join(entry_field_ids.mapped('field_name')),
                lazy=False,
            )

            entry_ids = [(5, False, False)]
            for entry_data in grouped_lines:
                entry_values = block._get_entry_values(
                    entry_data
                )
                if not entry_values:
                    continue

                entry_values.update({
                    'sequence': len(entry_ids),
                })
                entry_ids.append((0, False, entry_values))
            block.entry_ids = entry_ids

    @api.multi
    @api.depends('entry_ids')
    def _compute_is_multientry(self):
        for block in self:
            block.is_multientry = len(block.entry_ids) > 1

    @api.multi
    @api.depends('employee_id')
    def _compute_capacity(self):
        HrEmployee = self.env['hr.employee']
        Module = self.env['ir.module.module']

        project_timesheet_holidays = Module.sudo().search([
            ('name', '=', 'project_timesheet_holidays'),
            ('state', '=', 'installed'),
        ], limit=1)

        for block in self:
            tz = pytz.timezone(
                block.employee_id.resource_calendar_id.tz
            )
            from_datetime = datetime.combine(
                block.group_id.report_id.date_from,
                time.min
            ).replace(tzinfo=tz)
            to_datetime = datetime.combine(
                block.group_id.report_id.date_to,
                time.max
            ).replace(tzinfo=tz)

            employee_capacity = block.employee_id.get_work_days_data(
                from_datetime,
                to_datetime,
                compute_leaves=not project_timesheet_holidays,
            )['hours']

            if project_timesheet_holidays:
                employee_capacity -= HrEmployee.get_leave_days_data(
                    from_datetime,
                    to_datetime,
                    calendar=block.employee_id.resource_calendar_id
                )['hours']

            block.capacity = max(employee_capacity, 0)

    @api.multi
    @api.depends(
        'entry_ids.total_unit_amount_a',
        'entry_ids.total_unit_amount_b'
    )
    def _compute_total_unit_amount(self):
        for block in self:
            block.total_unit_amount_a = sum(
                block.entry_ids.mapped('total_unit_amount_a')
            )
            block.total_unit_amount_b = sum(
                block.entry_ids.mapped('total_unit_amount_b')
            )

    @api.multi
    @api.depends(
        'total_unit_amount_a',
        'total_unit_amount_b',
        'capacity'
    )
    def _compute_total_utilization(self):
        for block in self:
            if block.capacity != 0.0:
                total_utilization_a = (
                    block.total_unit_amount_a / block.capacity
                )
                total_utilization_b = (
                    block.total_unit_amount_b / block.capacity
                )
            else:
                total_utilization_a = float('+inf')
                total_utilization_b = float('+inf')
            block.total_utilization_a = total_utilization_a
            block.total_utilization_b = total_utilization_b

    @api.multi
    def _get_entries_domain(self):
        self.ensure_one()

        return [
            ('project_id', '!=', False),
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', fields.Date.to_string(
                self.group_id.report_id.date_from
            )),
            ('date', '<=', fields.Date.to_string(
                self.group_id.report_id.date_to
            )),
        ]

    @api.multi
    def _get_entry_values(self, grouped_lines):
        self.ensure_one()

        return {
            'scope': ustr(grouped_lines['__domain']),
        }


class HrUtilizationReportEntry(models.TransientModel):
    _name = 'hr.utilization.report.entry'
    _description = 'HR Utilization Report entry'
    _order = 'sequence, id'

    block_id = fields.Many2one(
        string='Block',
        comodel_name='hr.utilization.report.block',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    scope = fields.Char(
        string='Scope',
        required=True,
    )
    any_line_id = fields.Many2one(
        string='Account Analytics Lines',
        comodel_name='account.analytic.line',
        compute='_compute_any_line_id',
    )
    total_unit_amount_a = fields.Float(
        string='Total Quantity (A)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_unit_amount_b = fields.Float(
        string='Total Quantity (B)',
        compute='_compute_total_unit_amount',
        store=True,
    )
    total_utilization_a = fields.Float(
        string='Total Utilization (A)',
        compute='_compute_total_utilization',
        store=True,
    )
    total_utilization_b = fields.Float(
        string='Total Utilization (B)',
        compute='_compute_total_utilization',
        store=True,
    )

    @api.multi
    @api.depends('scope')
    def _compute_any_line_id(self):
        AccountAnalyticLine = self.env['account.analytic.line']

        for entry in self:
            entry.any_line_id = AccountAnalyticLine.search(
                safe_eval(entry.scope),
                limit=1,
            )

    @api.multi
    @api.depends('scope')
    def _compute_total_unit_amount(self):
        AccountAnalyticLine = self.env['account.analytic.line']
        uom_hour = self.env.ref('uom.product_uom_hour')

        for entry in self:
            report_id = entry.block_id.group_id.report_id
            line_ids = AccountAnalyticLine.search(safe_eval(entry.scope))

            if report_id.split_by_field_name:
                line_ids_a = line_ids.filtered(report_id.split_by_field_name)
                line_ids_b = line_ids - line_ids_a
            else:
                line_ids_a = line_ids
                line_ids_b = AccountAnalyticLine

            total_unit_amount_a = 0.0
            for line_id in line_ids_a:
                total_unit_amount_a += (
                    line_id.product_uom_id._compute_quantity(
                        line_id.unit_amount,
                        uom_hour
                    )
                )
            entry.total_unit_amount_a = total_unit_amount_a

            total_unit_amount_b = 0.0
            for line_id in line_ids_b:
                total_unit_amount_b += (
                    line_id.product_uom_id._compute_quantity(
                        line_id.unit_amount,
                        uom_hour
                    )
                )
            entry.total_unit_amount_b = total_unit_amount_b

    @api.multi
    @api.depends(
        'total_unit_amount_a',
        'total_unit_amount_b',
        'block_id.capacity'
    )
    def _compute_total_utilization(self):
        for entry in self:
            if entry.block_id.capacity != 0.0:
                total_utilization_a = (
                    entry.total_unit_amount_a / entry.block_id.capacity
                )
                total_utilization_b = (
                    entry.total_unit_amount_b / entry.block_id.capacity
                )
            else:
                total_utilization_a = float('+inf')
                total_utilization_b = float('+inf')
            entry.total_utilization_a = total_utilization_a
            entry.total_utilization_b = total_utilization_b

    @api.multi
    def render_value(self, field_name):
        self.ensure_one()

        AccountAnalyticLine = self.env['account.analytic.line']

        fields = AccountAnalyticLine.fields_get()
        converter_model = 'ir.qweb.field.' + fields[field_name]['type']
        converter = self.env.get(converter_model, self.env['ir.qweb.field'])

        return converter.record_to_html(self.any_line_id, field_name, {})


class Report(models.AbstractModel):
    _name = 'report.hr_utilization_report.report'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.utilization.report'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.utilization.report',
            'docs': docs,
        }

    @api.model
    def generate_xlsx_report(self, workbook, data, docs):
        for report_index, report in enumerate(docs):
            self._emit_report(workbook, report, report_index)

    @api.model
    def _emit_report(self, workbook, report, report_index):
        sheet = workbook.add_worksheet(
            _('Report %s') % (report_index + 1)
        )

        formats = self._create_workbook_formats(report, workbook)
        columns = self._get_columns(report)

        rows_emitted = self._emit_report_header(
            report,
            sheet,
            formats,
            columns
        )
        sheet.freeze_panes(rows_emitted, 0)

        group_row_indices = []
        for group in report.group_ids:

            if report.groupby_field_ids:
                group_row_indices.append(rows_emitted)
                rows_emitted += self._emit_group_header(
                    group,
                    report,
                    sheet,
                    formats,
                    columns,
                    rows_emitted
                )

            for block in group.block_ids:
                rows_emitted += self._emit_block(
                    block,
                    group,
                    report,
                    sheet,
                    formats,
                    columns,
                    rows_emitted
                )

            rows_emitted += 1

        self._emit_report_footer(
            report,
            sheet,
            formats,
            columns,
            rows_emitted,
            group_row_indices
        )

        self._post_emit(
            report,
            sheet,
            columns,
        )

    @api.model
    def _emit_report_header(self, report, sheet, formats, columns):
        if report.split_by_field_name:
            return self._emit_report_header_split(
                report,
                sheet,
                formats,
                columns
            )
        else:
            return self._emit_report_header_nosplit(
                report,
                sheet,
                formats,
                columns
            )

    @api.model
    def _emit_report_header_split(self, report, sheet, formats, columns):
        uom_hour = self.env.ref('uom.product_uom_hour')

        for column_index, entry_field in \
                enumerate(report.entry_field_ids):
            sheet.merge_range(
                0,
                column_index,
                1,
                column_index,
                entry_field.field_title,
                formats['header_title']
            )
        if report.utilization_format == 'percentage':
            sheet.merge_range(
                0,
                columns['utilization_a'],
                0,
                columns['total_utilization_b'],
                _('%s, %%') % (report.split_by_field_title),
                formats['header_title']
            )
            sheet.merge_range(
                1,
                columns['utilization_a'],
                1,
                columns['total_utilization_a'],
                _('Yes'),
                formats['header_title']
            )
            sheet.merge_range(
                1,
                columns['utilization_b'],
                1,
                columns['total_utilization_b'],
                _('No'),
                formats['header_title']
            )
        sheet.merge_range(
            0,
            columns['unit_amount_a'],
            0,
            columns['total_unit_amount_b'],
            _('Amount, %s') % (uom_hour.name),
            formats['header_title']
        )
        sheet.merge_range(
            1,
            columns['unit_amount_a'],
            1,
            columns['total_unit_amount_a'],
            _('Yes'),
            formats['header_title']
        )
        sheet.merge_range(
            1,
            columns['unit_amount_b'],
            1,
            columns['total_unit_amount_b'],
            _('No'),
            formats['header_title']
        )
        sheet.merge_range(
            0,
            columns['capacity'],
            1,
            columns['capacity'],
            _('Capacity, %s') % (uom_hour.name),
            formats['header_title']
        )
        return 2

    @api.model
    def _emit_report_header_nosplit(self, report, sheet, formats, columns):
        uom_hour = self.env.ref('uom.product_uom_hour')

        for column_index, entry_field in \
                enumerate(report.entry_field_ids):
            sheet.write(
                0,
                column_index,
                entry_field.field_title,
                formats['header_title']
            )
        if report.utilization_format == 'percentage':
            sheet.merge_range(
                0,
                columns['utilization_a'],
                0,
                columns['total_utilization_a'],
                _('Utilization, %'),
                formats['header_title']
            )
        sheet.merge_range(
            0,
            columns['unit_amount_a'],
            0,
            columns['total_unit_amount_a'],
            _('Amount, %s') % (uom_hour.name),
            formats['header_title']
        )
        sheet.write(
            0,
            columns['capacity'],
            _('Capacity, %s') % (uom_hour.name),
            formats['header_title']
        )
        return 1

    @api.model
    def _emit_group_header(
        self,
        group,
        report,
        sheet,
        formats,
        columns,
        rows_emitted
    ):
        group_rows_count = sum(map(
            lambda block_id: max(len(block_id.entry_ids), 1),
            group.block_ids
        ))

        if len(report.entry_field_ids) > 1:
            sheet.merge_range(
                rows_emitted,
                0,
                rows_emitted,
                len(report.entry_field_ids) - 1,
                group.name,
                formats['section_title']
            )
        else:
            sheet.write(
                rows_emitted,
                0,
                group.name,
                formats['section_title']
            )
        if report.utilization_format == 'percentage':
            sheet.merge_range(
                rows_emitted,
                columns['utilization_a'],
                rows_emitted,
                columns['total_utilization_a'],
                0,
                formats['section_total_utilization'],
            )
            sheet.write_formula(
                rows_emitted,
                columns['utilization_a'],
                '=%s/%s' % (
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['unit_amount_a']
                    ),
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['capacity']
                    ),
                ),
                formats['section_total_utilization'],
                group.total_utilization_a,
            )

            if report.split_by_field_name:
                sheet.merge_range(
                    rows_emitted,
                    columns['utilization_b'],
                    rows_emitted,
                    columns['total_utilization_b'],
                    0,
                    formats['section_total_utilization'],
                )
                sheet.write_formula(
                    rows_emitted,
                    columns['utilization_b'],
                    '=%s/%s' % (
                        xl_rowcol_to_cell(
                            rows_emitted,
                            columns['unit_amount_b']
                        ),
                        xl_rowcol_to_cell(
                            rows_emitted,
                            columns['capacity']
                        ),
                    ),
                    formats['section_total_utilization'],
                    group.total_utilization_b,
                )
        sheet.merge_range(
            rows_emitted,
            columns['unit_amount_a'],
            rows_emitted,
            columns['total_unit_amount_a'],
            0,
            formats['section_total_amount'],
        )
        sheet.write_formula(
            rows_emitted,
            columns['unit_amount_a'],
            '=SUM(%s:%s)' % (
                xl_rowcol_to_cell(
                    rows_emitted + 1,
                    columns['total_unit_amount_a']
                ),
                xl_rowcol_to_cell(
                    rows_emitted + group_rows_count,
                    columns['total_unit_amount_a']
                ),
            ),
            formats['section_total_amount'],
            self._convert_time_num_format(
                report,
                group.total_unit_amount_a
            ),
        )
        if report.split_by_field_name:
            sheet.merge_range(
                rows_emitted,
                columns['unit_amount_b'],
                rows_emitted,
                columns['total_unit_amount_b'],
                0,
                formats['section_total_amount'],
            )
            sheet.write_formula(
                rows_emitted,
                columns['unit_amount_b'],
                '=SUM(%s:%s)' % (
                    xl_rowcol_to_cell(
                        rows_emitted + 1,
                        columns['total_unit_amount_b']
                    ),
                    xl_rowcol_to_cell(
                        rows_emitted + group_rows_count,
                        columns['total_unit_amount_b']
                    ),
                ),
                formats['section_total_amount'],
                self._convert_time_num_format(
                    report,
                    group.total_unit_amount_b
                ),
            )
        sheet.write_formula(
            rows_emitted,
            columns['capacity'],
            '=SUM(%s:%s)' % (
                xl_rowcol_to_cell(
                    rows_emitted + 1,
                    columns['capacity']
                ),
                xl_rowcol_to_cell(
                    rows_emitted + group_rows_count,
                    columns['capacity']
                ),
            ),
            formats['section_total_capacity'],
            self._convert_time_num_format(
                report,
                group.total_capacity
            ),
        )

        return 1

    @api.model
    def _emit_block(
        self,
        block,
        group,
        report,
        sheet,
        formats,
        columns,
        rows_emitted
    ):
        if not block.entry_ids:
            return self._emit_block_empty(
                block,
                group,
                report,
                sheet,
                formats,
                columns,
                rows_emitted
            )

        entry_rows_emitted = 0
        for entry in block.entry_ids:
            entry_rows_emitted += self._emit_entry(
                entry,
                block,
                group,
                report,
                sheet,
                formats,
                columns,
                rows_emitted,
                rows_emitted + entry_rows_emitted
            )

        for column_index, entry_field in \
                enumerate(report.entry_field_ids):
            if entry_field.field_name != 'employee_id':
                continue
            if entry_rows_emitted > 1:
                sheet.merge_range(
                    rows_emitted,
                    column_index,
                    rows_emitted + entry_rows_emitted - 1,
                    column_index,
                    block.employee_id.name,
                    formats['block_employee']
                )
            else:
                sheet.write_string(
                    rows_emitted,
                    column_index,
                    block.employee_id.name,
                    formats['block_employee']
                )
            break

        if entry_rows_emitted > 1:
            sheet.merge_range(
                rows_emitted,
                columns['total_unit_amount_a'],
                rows_emitted + entry_rows_emitted - 1,
                columns['total_unit_amount_a'],
                0,
                formats['block_total_amount']
            )
        sheet.write_formula(
            rows_emitted,
            columns['total_unit_amount_a'],
            '=SUM(%s:%s)' % (
                xl_rowcol_to_cell(
                    rows_emitted,
                    columns['unit_amount_a']
                ),
                xl_rowcol_to_cell(
                    rows_emitted + entry_rows_emitted - 1,
                    columns['unit_amount_a']
                ),
            ),
            formats['block_total_amount'],
            self._convert_time_num_format(
                report,
                block.total_unit_amount_a
            ),
        )

        if report.utilization_format == 'percentage':
            if entry_rows_emitted > 1:
                sheet.merge_range(
                    rows_emitted,
                    columns['total_utilization_a'],
                    rows_emitted + entry_rows_emitted - 1,
                    columns['total_utilization_a'],
                    0,
                    formats['block_total_utilization']
                )
            sheet.write_formula(
                rows_emitted,
                columns['total_utilization_a'],
                '=SUM(%s:%s)' % (
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['utilization_a']
                    ),
                    xl_rowcol_to_cell(
                        rows_emitted + entry_rows_emitted - 1,
                        columns['utilization_a']
                    ),
                ),
                formats['block_total_utilization'],
                block.total_utilization_a
            )

        if report.split_by_field_name:
            if entry_rows_emitted > 1:
                sheet.merge_range(
                    rows_emitted,
                    columns['total_unit_amount_b'],
                    rows_emitted + entry_rows_emitted - 1,
                    columns['total_unit_amount_b'],
                    0,
                    formats['block_total_amount']
                )
            sheet.write_formula(
                rows_emitted,
                columns['total_unit_amount_b'],
                '=SUM(%s:%s)' % (
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['unit_amount_b']
                    ),
                    xl_rowcol_to_cell(
                        rows_emitted + entry_rows_emitted - 1,
                        columns['unit_amount_b']
                    ),
                ),
                formats['block_total_amount'],
                self._convert_time_num_format(
                    report,
                    block.total_unit_amount_b
                ),
            )

            if report.utilization_format == 'percentage':
                if entry_rows_emitted > 1:
                    sheet.merge_range(
                        rows_emitted,
                        columns['total_utilization_b'],
                        rows_emitted + entry_rows_emitted - 1,
                        columns['total_utilization_b'],
                        0,
                        formats['block_total_utilization']
                    )
                sheet.write_formula(
                    rows_emitted,
                    columns['total_utilization_b'],
                    '=SUM(%s:%s)' % (
                        xl_rowcol_to_cell(
                            rows_emitted,
                            columns['utilization_b']
                        ),
                        xl_rowcol_to_cell(
                            rows_emitted + entry_rows_emitted - 1,
                            columns['utilization_b']
                        ),
                    ),
                    formats['block_total_utilization'],
                    block.total_utilization_b
                )

        if entry_rows_emitted > 1:
            sheet.merge_range(
                rows_emitted,
                columns['capacity'],
                rows_emitted + entry_rows_emitted - 1,
                columns['capacity'],
                self._convert_time_num_format(
                    report,
                    block.capacity
                ),
                formats['block_capacity']
            )
        else:
            sheet.write(
                rows_emitted,
                columns['capacity'],
                self._convert_time_num_format(
                    report,
                    block.capacity
                ),
                formats['block_capacity']
            )

        return entry_rows_emitted

    @api.model
    def _emit_block_empty(
        self,
        block,
        group,
        report,
        sheet,
        formats,
        columns,
        rows_emitted
    ):
        for column_index, entry_field in \
                enumerate(report.entry_field_ids):
            if entry_field.field_name == 'employee_id':
                sheet.write_string(
                    rows_emitted,
                    column_index,
                    block.employee_id.name,
                    formats['block_employee']
                )
            else:
                sheet.write_blank(
                    rows_emitted,
                    column_index,
                    '',
                    formats['cell_generic']
                )

        sheet.write(
            rows_emitted,
            columns['unit_amount_a'],
            0,
            formats['entry_total_amount'],
        )
        sheet.write_formula(
            rows_emitted,
            columns['total_unit_amount_a'],
            '=%s' % (
                xl_rowcol_to_cell(
                    rows_emitted,
                    columns['unit_amount_a']
                ),
            ),
            formats['block_total_amount'],
            self._convert_time_num_format(
                report,
                block.total_unit_amount_a
            ),
        )

        if report.utilization_format == 'percentage':
            sheet.write(
                rows_emitted,
                columns['utilization_a'],
                0,
                formats['entry_total_utilization'],
            )
            sheet.write_formula(
                rows_emitted,
                columns['total_utilization_a'],
                '=%s' % (
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['utilization_a']
                    ),
                ),
                formats['block_total_utilization'],
                block.total_utilization_a
            )

        if report.split_by_field_name:
            sheet.write(
                rows_emitted,
                columns['unit_amount_b'],
                0,
                formats['entry_total_amount'],
            )
            sheet.write_formula(
                rows_emitted,
                columns['total_unit_amount_b'],
                '=%s' % (
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['unit_amount_b']
                    ),
                ),
                formats['block_total_amount'],
                self._convert_time_num_format(
                    report,
                    block.total_unit_amount_b
                ),
            )

            if report.utilization_format == 'percentage':
                sheet.write(
                    rows_emitted,
                    columns['utilization_b'],
                    0,
                    formats['entry_total_utilization'],
                )
                sheet.write_formula(
                    rows_emitted,
                    columns['total_utilization_b'],
                    '=%s' % (
                        xl_rowcol_to_cell(
                            rows_emitted,
                            columns['utilization_b']
                        ),
                    ),
                    formats['block_total_utilization'],
                    block.total_utilization_b
                )

        sheet.write(
            rows_emitted,
            columns['capacity'],
            self._convert_time_num_format(
                report,
                block.capacity
            ),
            formats['block_capacity']
        )

        return 1

    @api.model
    def _emit_entry(
        self,
        entry,
        block,
        group,
        report,
        sheet,
        formats,
        columns,
        block_row_index,
        rows_emitted
    ):
        for column_index, entry_field in \
                enumerate(report.entry_field_ids):
            if entry_field.field_name == 'employee_id':
                continue

            self._render_value_cell(
                rows_emitted,
                column_index,
                sheet,
                formats,
                entry,
                entry_field
            )
        if report.utilization_format == 'percentage':
            sheet.write_formula(
                rows_emitted,
                columns['utilization_a'],
                '=%s/%s' % (
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['unit_amount_a']
                    ),
                    xl_rowcol_to_cell(
                        block_row_index,
                        columns['capacity']
                    ),
                ),
                formats['entry_total_utilization'],
                entry.total_utilization_a,
            )

            if report.split_by_field_name:
                sheet.write_formula(
                    rows_emitted,
                    columns['utilization_b'],
                    '=%s/%s' % (
                        xl_rowcol_to_cell(
                            rows_emitted,
                            columns['unit_amount_b']
                        ),
                        xl_rowcol_to_cell(
                            block_row_index,
                            columns['capacity']
                        ),
                    ),
                    formats['entry_total_utilization'],
                    entry.total_utilization_b,
                )
        sheet.write_number(
            rows_emitted,
            columns['unit_amount_a'],
            self._convert_time_num_format(
                report,
                entry.total_unit_amount_a
            ),
            formats['entry_total_amount']
        )
        if report.split_by_field_name:
            sheet.write_number(
                rows_emitted,
                columns['unit_amount_b'],
                self._convert_time_num_format(
                    report,
                    entry.total_unit_amount_b
                ),
                formats['entry_total_amount']
            )

        return 1

    @api.model
    def _emit_report_footer(
        self,
        report,
        sheet,
        formats,
        columns,
        rows_emitted,
        group_row_indices
    ):
        if len(report.entry_field_ids) > 1:
            sheet.merge_range(
                rows_emitted,
                0,
                rows_emitted,
                len(report.entry_field_ids) - 1,
                _('Total'),
                formats['report_total_caption']
            )
        else:
            sheet.write(
                rows_emitted,
                0,
                _('Total'),
                formats['report_total_caption']
            )
        if report.utilization_format == 'percentage':
            sheet.merge_range(
                rows_emitted,
                columns['utilization_a'],
                rows_emitted,
                columns['total_utilization_a'],
                0,
                formats['report_total_utilization'],
            )
            sheet.write_formula(
                rows_emitted,
                columns['utilization_a'],
                '=%s/%s' % (
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['unit_amount_a']
                    ),
                    xl_rowcol_to_cell(
                        rows_emitted,
                        columns['capacity']
                    ),
                ),
                formats['report_total_utilization'],
                report.total_utilization_a,
            )

            if report.split_by_field_name:
                sheet.merge_range(
                    rows_emitted,
                    columns['utilization_b'],
                    rows_emitted,
                    columns['total_utilization_b'],
                    0,
                    formats['report_total_utilization'],
                )
                sheet.write_formula(
                    rows_emitted,
                    columns['utilization_b'],
                    '=%s/%s' % (
                        xl_rowcol_to_cell(
                            rows_emitted,
                            columns['unit_amount_b']
                        ),
                        xl_rowcol_to_cell(
                            rows_emitted,
                            columns['capacity']
                        ),
                    ),
                    formats['report_total_utilization'],
                    report.total_utilization_b,
                )
        if group_row_indices:
            sheet.merge_range(
                rows_emitted,
                columns['unit_amount_a'],
                rows_emitted,
                columns['total_unit_amount_a'],
                0,
                formats['report_total_amount'],
            )
            sheet.write_formula(
                rows_emitted,
                columns['unit_amount_a'],
                '=SUM(%s)' % ('+'.join(map(
                    lambda x: xl_rowcol_to_cell(
                        x,
                        columns['unit_amount_a']
                    ),
                    group_row_indices
                ))),
                formats['report_total_amount'],
                self._convert_time_num_format(
                    report,
                    report.total_unit_amount_a
                ),
            )
        else:
            sheet.merge_range(
                rows_emitted,
                columns['unit_amount_a'],
                rows_emitted,
                columns['total_unit_amount_a'],
                0,
                formats['report_total_amount'],
            )
            sheet.write_formula(
                rows_emitted,
                columns['unit_amount_a'],
                '=SUM(%s:%s)' % (
                    xl_rowcol_to_cell(
                        1,
                        columns['unit_amount_a']
                    ),
                    xl_rowcol_to_cell(
                        rows_emitted - 1,
                        columns['unit_amount_a']
                    ),
                ),
                formats['report_total_amount'],
                self._convert_time_num_format(
                    report,
                    report.total_unit_amount_a
                ),
            )
        if report.split_by_field_name:
            if group_row_indices:
                sheet.merge_range(
                    rows_emitted,
                    columns['unit_amount_b'],
                    rows_emitted,
                    columns['total_unit_amount_b'],
                    0,
                    formats['report_total_amount']
                )
                sheet.write_formula(
                    rows_emitted,
                    columns['unit_amount_b'],
                    '=SUM(%s)' % ('+'.join(map(
                        lambda x: xl_rowcol_to_cell(
                            x,
                            columns['unit_amount_b']
                        ),
                        group_row_indices
                    ))),
                    formats['report_total_amount'],
                    self._convert_time_num_format(
                        report,
                        report.total_unit_amount_b
                    ),
                )
            else:
                sheet.merge_range(
                    rows_emitted,
                    columns['unit_amount_b'],
                    rows_emitted,
                    columns['total_unit_amount_b'],
                    0,
                    formats['report_total_amount'],
                )
                sheet.write_formula(
                    rows_emitted,
                    columns['unit_amount_b'],
                    '=SUM(%s:%s)' % (
                        xl_rowcol_to_cell(
                            1,
                            columns['unit_amount_b']
                        ),
                        xl_rowcol_to_cell(
                            rows_emitted - 1,
                            columns['unit_amount_b']
                        ),
                    ),
                    formats['report_total_amount'],
                    self._convert_time_num_format(
                        report,
                        report.total_unit_amount_b
                    ),
                )

        if group_row_indices:
            sheet.write_formula(
                rows_emitted,
                columns['capacity'],
                '=SUM(%s)' % ('+'.join(map(
                    lambda x: xl_rowcol_to_cell(x, columns['capacity']),
                    group_row_indices
                ))),
                formats['report_total_capacity'],
                self._convert_time_num_format(
                    report,
                    report.total_capacity
                ),
            )
        else:
            sheet.write_formula(
                rows_emitted,
                columns['capacity'],
                '=SUM(%s:%s)' % (
                    xl_rowcol_to_cell(
                        1,
                        columns['capacity']
                    ),
                    xl_rowcol_to_cell(
                        rows_emitted - 1,
                        columns['capacity']
                    ),
                ),
                formats['report_total_capacity'],
                self._convert_time_num_format(
                    report,
                    report.total_capacity
                ),
            )

    @api.model
    def _post_emit(self, report, sheet, columns):
        if report.utilization_format == 'percentage':
            sheet.set_column(
                columns['unit_amount_a'],
                columns['unit_amount_a'],
                options={
                    'hidden': True,
                }
            )
            sheet.set_column(
                columns['total_unit_amount_a'],
                columns['total_unit_amount_a'],
                options={
                    'hidden': True,
                }
            )

            if report.split_by_field_name:
                sheet.set_column(
                    columns['unit_amount_b'],
                    columns['unit_amount_b'],
                    options={
                        'hidden': True,
                    }
                )
                sheet.set_column(
                    columns['total_unit_amount_b'],
                    columns['total_unit_amount_b'],
                    options={
                        'hidden': True,
                    }
                )

            if not report.has_multientry_blocks:
                sheet.set_column(
                    columns['total_utilization_a'],
                    columns['total_utilization_a'],
                    options={
                        'hidden': True,
                    }
                )

                if report.split_by_field_name:
                    sheet.set_column(
                        columns['total_utilization_b'],
                        columns['total_utilization_b'],
                        options={
                            'hidden': True,
                        }
                    )
        else:
            if not report.has_multientry_blocks:
                sheet.set_column(
                    columns['total_unit_amount_a'],
                    columns['total_unit_amount_a'],
                    options={
                        'hidden': True,
                    }
                )

                if report.split_by_field_name:
                    sheet.set_column(
                        columns['total_unit_amount_b'],
                        columns['total_unit_amount_b'],
                        options={
                            'hidden': True,
                        }
                    )

    @api.model
    def _create_workbook_formats(self, report, workbook):
        time_num_format = self._get_time_num_format(report)

        return {
            'header_title': workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
            }),
            'section_title': workbook.add_format({
                'italic': True,
            }),
            'section_total_utilization': workbook.add_format({
                'num_format': '0.0%',
                'italic': True,
            }),
            'section_total_amount': workbook.add_format({
                'num_format': time_num_format,
                'italic': True,
            }),
            'section_total_capacity': workbook.add_format({
                'num_format': time_num_format,
                'italic': True,
            }),
            'block_employee': workbook.add_format({
                'align': 'left',
                'valign': 'vcenter',
            }),
            'block_total_utilization': workbook.add_format({
                'num_format': '0.0%',
                'italic': True,
                'valign': 'vcenter',
            }),
            'block_total_amount': workbook.add_format({
                'num_format': time_num_format,
                'italic': True,
                'valign': 'vcenter',
            }),
            'block_capacity': workbook.add_format({
                'num_format': time_num_format,
                'valign': 'vcenter',
            }),
            'report_total_caption': workbook.add_format({
                'bold': True,
                'align': 'right',
            }),
            'report_total_utilization': workbook.add_format({
                'num_format': '0.0%',
                'bold': True,
            }),
            'report_total_amount': workbook.add_format({
                'num_format': time_num_format,
                'bold': True,
            }),
            'report_total_capacity': workbook.add_format({
                'num_format': time_num_format,
                'bold': True,
            }),
            'cell_generic': workbook.add_format({
                'align': 'left',
            }),
            'cell_date': workbook.add_format({
                'num_format': 'd mmm yyyy',
                'align': 'left',
            }),
            'cell_datetime': workbook.add_format({
                'num_format': 'd mmm yyyy hh:mm',
                'align': 'left',
            }),
            'entry_total_utilization': workbook.add_format({
                'num_format': '0.0%',
            }),
            'entry_total_amount': workbook.add_format({
                'num_format': time_num_format,
            }),
        }

    @api.model
    def _get_columns(self, report):
        result = {}

        columns_emitted = len(report.entry_field_ids)

        if report.utilization_format == 'percentage':
            result['utilization_a'] = columns_emitted
            columns_emitted += 1

            result['total_utilization_a'] = columns_emitted
            columns_emitted += 1

            if report.split_by_field_name:
                result['utilization_b'] = columns_emitted
                columns_emitted += 1

                result['total_utilization_b'] = columns_emitted
                columns_emitted += 1

        result['unit_amount_a'] = columns_emitted
        columns_emitted += 1

        result['total_unit_amount_a'] = columns_emitted
        columns_emitted += 1

        if report.split_by_field_name:
            result['unit_amount_b'] = columns_emitted
            columns_emitted += 1

            result['total_unit_amount_b'] = columns_emitted
            columns_emitted += 1

        result['capacity'] = columns_emitted
        columns_emitted += 1

        return result

    @api.model
    def _get_time_num_format(self, report):
        if report.time_format == 'decimal':
            return '0.00'
        elif report.time_format == 'hh_mm':
            return '[h]:mm'
        elif report.time_format == 'hh_mm_ss':
            return '[h]:mm:ss'

    @api.model
    def _convert_time_num_format(self, report, value):
        if report.time_format in ['hh_mm', 'hh_mm_ss']:
            return value / 24.0
        return value

    @api.model
    def _render_value_cell(self, row, col, sheet, formats, entry, field):
        raw_value = entry.any_line_id[field.field_name]
        value = entry.render_value(field.field_name) or ''
        if field.field_type == 'datetime':
            sheet.write_datetime(
                row,
                col,
                raw_value,
                formats['cell_datetime']
            )
        elif field.field_type == 'date':
            sheet.write_datetime(
                row,
                col,
                raw_value,
                formats['cell_date']
            )
        else:
            sheet.write(
                row,
                col,
                html.unescape(value),
                formats['cell_generic']
            )
