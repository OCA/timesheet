# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv.expression import TRUE_DOMAIN
from odoo.tools import ustr
from odoo.tools.safe_eval import safe_eval

import html
from functools import reduce
from xlsxwriter.utility import xl_rowcol_to_cell


class HrTimesheetReport(models.TransientModel):
    _name = 'hr.timesheet.report'
    _description = 'HR Timesheet Report'

    line_ids = fields.Many2many(
        string='Account Analytics Lines',
        comodel_name='account.analytic.line',
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
    groupby_field_ids = fields.One2many(
        string='Group-By Fields',
        comodel_name='hr.timesheet.report.field.groupby',
        inverse_name='report_id',
    )
    entry_field_ids = fields.One2many(
        string='Entry Fields',
        comodel_name='hr.timesheet.report.field.entry',
        inverse_name='report_id',
    )
    time_format = fields.Selection(
        string='Time format',
        selection=lambda self: self._selection_time_format(),
        required=True,
    )
    group_ids = fields.One2many(
        string='Groups',
        comodel_name='hr.timesheet.report.group',
        inverse_name='report_id',
        compute='_compute_group_ids',
        store=True,
    )
    total_unit_amount = fields.Float(
        string='Total Quantity',
        compute='_compute_total_unit_amount',
        store=True,
    )

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
    @api.depends(
        'line_ids',
        'date_from',
        'date_to',
        'project_ids',
        'task_ids',
        'employee_ids',
        'employee_category_ids',
        'department_ids',
        'groupby_field_ids',
        'entry_field_ids',
    )
    def _compute_group_ids(self):
        AccountAnalyticLine = self.env['account.analytic.line']

        for report in self:
            group_ids = [(5, False, False)]

            if report.groupby_field_ids:
                grouped_lines = AccountAnalyticLine.read_group(
                    domain=report._get_domain(),
                    fields=list(set(
                        report.entry_field_ids.mapped('field_name')
                    ) | set(
                        report.groupby_field_ids.mapped('field_name')
                    )),
                    groupby=report.groupby_field_ids.mapped('groupby'),
                    orderby=', '.join(
                        report.groupby_field_ids.mapped('field_name'),
                    ),
                    lazy=False,
                )

                for group_data in grouped_lines:
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
                    'scope': ustr(report._get_domain()),
                }))
            report.group_ids = group_ids

    @api.multi
    def _get_group_values(self, grouped_lines):
        self.ensure_one()

        name_parts = []
        for field in self.groupby_field_ids:
            name_part = grouped_lines.get(field.field_name, None)
            if not name_part:
                name_part = _('%s not set') % (field.field_title)
            else:
                name_part = name_part[1]
            name_parts.append(name_part)

        return {
            'name': reduce(
                lambda l, r: _('{l} » {r}').format(l=l, r=r),
                name_parts
            ),
            'scope': ustr(grouped_lines['__domain']),
        }

    @api.multi
    @api.depends('group_ids.total_unit_amount')
    def _compute_total_unit_amount(self):
        for report in self:
            report.total_unit_amount = sum(
                report.group_ids.mapped('total_unit_amount')
            )

    @api.multi
    def _get_domain(self):
        self.ensure_one()

        if self.line_ids:
            return [('id', 'in', self.line_ids.ids)]

        query = [('project_id', '!=', False)]
        if self.date_from:
            query.append(('date', '>=', fields.Date.to_string(self.date_from)))
        if self.date_to:
            query.append(('date', '<=', fields.Date.to_string(self.date_to)))
        if self.project_ids:
            query.append(('project_id', 'in', self.project_ids.ids))
        if self.task_ids:
            query.append(('task_id', 'in', self.task_ids.ids))
        employee_ids = (
            self.employee_ids
            | self.employee_category_ids.mapped('employee_ids')
        )
        if employee_ids:
            query.append(('employee_id', 'in', employee_ids.ids))
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

        report_name = 'hr_timesheet_report.report'

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


class HrTimesheetReportAbstractField(models.AbstractModel):
    _name = 'hr.timesheet.report.field'
    _description = 'HR Timesheet Report field'
    _order = 'sequence, id'

    report_id = fields.Many2one(
        string='Report',
        comodel_name='hr.timesheet.report',
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


class HrTimesheetReportGroupByField(models.TransientModel):
    _name = 'hr.timesheet.report.field.groupby'
    _description = 'HR Timesheet Report field (groupby)'
    _inherit = 'hr.timesheet.report.field'


class HrTimesheetReportEntryField(models.TransientModel):
    _name = 'hr.timesheet.report.field.entry'
    _description = 'HR Timesheet Report field (entry)'
    _inherit = 'hr.timesheet.report.field'

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


class HrTimesheetReportGroup(models.TransientModel):
    _name = 'hr.timesheet.report.group'
    _description = 'HR Timesheet Report group'
    _order = 'sequence, id'

    report_id = fields.Many2one(
        string='Report',
        comodel_name='hr.timesheet.report',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    scope = fields.Char(
        string='Scope',
    )
    name = fields.Char()
    entry_ids = fields.One2many(
        string='Entries',
        comodel_name='hr.timesheet.report.entry',
        inverse_name='group_id',
        compute='_compute_entry_ids',
        store=True,
    )
    total_unit_amount = fields.Float(
        string='Total Quantity',
        compute='_compute_total_unit_amount',
        store=True,
    )

    @api.multi
    @api.depends(
        'scope',
        'report_id.groupby_field_ids',
        'report_id.entry_field_ids',
    )
    def _compute_entry_ids(self):
        AccountAnalyticLine = self.env['account.analytic.line']

        for group in self:
            grouped_lines = AccountAnalyticLine.read_group(
                domain=safe_eval(group.scope) if group.scope else TRUE_DOMAIN,
                fields=list({'id'} | set(
                    group.report_id.entry_field_ids.mapped('field_name')
                )),
                groupby=group.report_id.entry_field_ids.mapped('groupby'),
                orderby=', '.join(
                    group.report_id.entry_field_ids.mapped('field_name'),
                ),
                lazy=False,
            )

            entry_ids = [(5, False, False)]
            for entry_data in grouped_lines:
                entry_values = group._get_entry_values(
                    entry_data
                )
                if not entry_values:
                    continue

                entry_values.update({
                    'sequence': len(entry_ids),
                })
                entry_ids.append((0, False, entry_values))
            group.entry_ids = entry_ids

    @api.multi
    @api.depends('entry_ids.total_unit_amount')
    def _compute_total_unit_amount(self):
        for group in self:
            group.total_unit_amount = sum(
                group.entry_ids.mapped('total_unit_amount')
            )

    @api.multi
    def _get_entry_values(self, grouped_lines):
        self.ensure_one()
        return {
            'scope': ustr(grouped_lines['__domain']),
        }


class HrTimesheetReportEntry(models.TransientModel):
    _name = 'hr.timesheet.report.entry'
    _description = 'HR Timesheet Report entry'
    _order = 'sequence, id'

    group_id = fields.Many2one(
        string='Group',
        comodel_name='hr.timesheet.report.group',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    scope = fields.Char(
        string='Scope',
    )
    any_line_id = fields.Many2one(
        string='Account Analytics Lines',
        comodel_name='account.analytic.line',
        compute='_compute_any_line_id',
    )
    total_unit_amount = fields.Float(
        string='Total Quantity',
        compute='_compute_total_unit_amount',
        store=True,
    )

    @api.multi
    @api.depends('scope')
    def _compute_any_line_id(self):
        AccountAnalyticLine = self.env['account.analytic.line']

        for entry in self:
            entry.any_line_id = AccountAnalyticLine.search(
                safe_eval(entry.scope) if entry.scope else TRUE_DOMAIN,
                limit=1,
            )

    @api.multi
    @api.depends('scope')
    def _compute_total_unit_amount(self):
        AccountAnalyticLine = self.env['account.analytic.line']
        uom_hour = self.env.ref('uom.product_uom_hour')

        for entry in self:
            total_unit_amount = 0.0
            line_ids = AccountAnalyticLine.search(
                safe_eval(entry.scope) if entry.scope else TRUE_DOMAIN
            )
            for line_id in line_ids:
                total_unit_amount += line_id.product_uom_id._compute_quantity(
                    line_id.unit_amount,
                    uom_hour
                )
            entry.total_unit_amount = total_unit_amount

    @api.multi
    def render_value(self, field_name):
        self.ensure_one()

        AccountAnalyticLine = self.env['account.analytic.line']

        fields = AccountAnalyticLine.fields_get()
        converter_model = 'ir.qweb.field.' + fields[field_name]['type']
        converter = self.env.get(converter_model, self.env['ir.qweb.field'])

        return converter.record_to_html(self.any_line_id, field_name, {})


class Report(models.AbstractModel):
    _name = 'report.hr_timesheet_report.report'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.timesheet.report'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.timesheet.report',
            'docs': docs,
        }

    @api.model
    def generate_xlsx_report(self, workbook, data, docs):
        uom_hour = self.env.ref('uom.product_uom_hour')

        for report_index, report in enumerate(docs):
            sheet = workbook.add_worksheet(
                _('Report %s') % (report_index + 1)
            )

            formats = self._create_workbook_formats(report, workbook)

            amount_column_index = len(report.entry_field_ids)

            for column_index, entry_field in enumerate(report.entry_field_ids):
                sheet.write(
                    0,
                    column_index,
                    entry_field.field_title,
                    formats['header_title']
                )
            sheet.write(
                0,
                amount_column_index,
                uom_hour.name,
                formats['header_title']
            )
            sheet.freeze_panes(1, 0)
            rows_emitted = 1

            section_row_indices = []
            for group in report.group_ids:
                if group.name:
                    section_row_indices.append(rows_emitted)

                    if amount_column_index > 1:
                        sheet.merge_range(
                            rows_emitted,
                            0,
                            rows_emitted,
                            amount_column_index - 1,
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
                    sheet.write_formula(
                        rows_emitted,
                        amount_column_index,
                        '=SUM(%s:%s)' % (
                            xl_rowcol_to_cell(
                                rows_emitted + 1,
                                amount_column_index
                            ),
                            xl_rowcol_to_cell(
                                rows_emitted + len(group.entry_ids),
                                amount_column_index
                            ),
                        ),
                        formats['section_total'],
                        self._convert_amount_num_format(
                            report,
                            group.total_unit_amount
                        ),
                    )
                    rows_emitted += 1

                for entry in group.entry_ids:
                    for column_index, entry_field in \
                            enumerate(report.entry_field_ids):
                        self._render_value_cell(
                            rows_emitted,
                            column_index,
                            sheet,
                            formats,
                            entry,
                            entry_field
                        )
                    sheet.write_number(
                        rows_emitted,
                        amount_column_index,
                        self._convert_amount_num_format(
                            report,
                            entry.total_unit_amount
                        ),
                        formats['entry_total']
                    )

                    rows_emitted += 1

                rows_emitted += 1

            if amount_column_index > 1:
                sheet.merge_range(
                    rows_emitted,
                    0,
                    rows_emitted,
                    amount_column_index - 1,
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
            if section_row_indices:
                sheet.write_formula(
                    rows_emitted,
                    amount_column_index,
                    '=SUM(%s)' % ('+'.join(map(
                        lambda x: xl_rowcol_to_cell(x, amount_column_index),
                        section_row_indices
                    ))),
                    formats['report_total_amount'],
                    self._convert_amount_num_format(
                        report,
                        report.total_unit_amount
                    ),
                )
            else:
                sheet.write_formula(
                    rows_emitted,
                    amount_column_index,
                    '=SUM(%s:%s)' % (
                        xl_rowcol_to_cell(
                            1,
                            amount_column_index
                        ),
                        xl_rowcol_to_cell(
                            rows_emitted - 2,
                            amount_column_index
                        ),
                    ),
                    formats['report_total_amount'],
                    self._convert_amount_num_format(
                        report,
                        report.total_unit_amount
                    ),
                )

    @api.model
    def _create_workbook_formats(self, report, workbook):
        amount_num_format = self._get_amount_num_format(report)

        return {
            'header_title': workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
            }),
            'section_title': workbook.add_format({
                'italic': True,
            }),
            'section_total': workbook.add_format({
                'num_format': amount_num_format,
                'italic': True,
            }),
            'report_total_caption': workbook.add_format({
                'bold': True,
                'align': 'right',
            }),
            'report_total_amount': workbook.add_format({
                'num_format': amount_num_format,
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
            'entry_total': workbook.add_format({
                'num_format': amount_num_format,
            }),
        }

    @api.model
    def _get_amount_num_format(self, report):
        if report.time_format == 'decimal':
            return '0.00'
        elif report.time_format == 'hh_mm':
            return '[h]:mm'
        elif report.time_format == 'hh_mm_ss':
            return '[h]:mm:ss'

    @api.model
    def _convert_amount_num_format(self, report, amount):
        if report.time_format in ['hh_mm', 'hh_mm_ss']:
            return amount / 24.0
        return amount

    @api.model
    def _render_value_cell(self, row, col, sheet, formats, entry, field):
        raw_value = entry.any_line_id[field.field_name]
        value = entry.render_value(field.field_name)
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
