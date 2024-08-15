# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import babel.dates
import logging
import re
from collections import namedtuple
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, WEEKLY

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

empty_name = '/'


class Sheet(models.Model):
    _name = 'hr_timesheet.sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _table = 'hr_timesheet_sheet'
    _order = 'id desc'
    _description = 'Timesheet Sheet'

    def _default_date_start(self):
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.sheet_range or WEEKLY
        today = fields.Date.context_today(self)
        if r == WEEKLY:
            if user.company_id.timesheet_week_start:
                delta = relativedelta(
                    weekday=int(user.company_id.timesheet_week_start),
                    days=6)
            else:
                delta = relativedelta(days=today.weekday())
            return today - delta
        elif r == MONTHLY:
            return today + relativedelta(day=1)
        return today

    def _default_date_end(self):
        user = self.env['res.users'].browse(self.env.uid)
        r = user.company_id and user.company_id.sheet_range or WEEKLY
        today = fields.Date.context_today(self)
        if r == WEEKLY:
            if user.company_id.timesheet_week_start:
                delta = relativedelta(weekday=(int(
                    user.company_id.timesheet_week_start) + 6) % 7)
            else:
                delta = relativedelta(days=6-today.weekday())
            return today + delta
        elif r == MONTHLY:
            return today + relativedelta(months=1, day=1, days=-1)
        return today

    def _default_employee(self):
        company = self.env['res.company']._company_default_get()
        return self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid),
            ('company_id', 'in', [company.id, False]),
        ], limit=1, order="company_id ASC")

    name = fields.Char(
        compute='_compute_name',
        context_dependent=True,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        default=lambda self: self._default_employee(),
        required=True,
        readonly=True,
        states={'new': [('readonly', False)]},
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        related='employee_id.user_id',
        string='User',
        store=True,
        readonly=True,
    )
    date_start = fields.Date(
        string='Date From',
        default=lambda self: self._default_date_start(),
        required=True,
        index=True,
        readonly=True,
        states={'new': [('readonly', False)]},
    )
    date_end = fields.Date(
        string='Date To',
        default=lambda self: self._default_date_end(),
        required=True,
        index=True,
        readonly=True,
        states={'new': [('readonly', False)]},
    )
    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='sheet_id',
        string='Timesheets',
        readonly=True,
        states={
            'new': [('readonly', False)],
            'draft': [('readonly', False)],
        },
    )
    line_ids = fields.One2many(
        comodel_name='hr_timesheet.sheet.line',
        compute='_compute_line_ids',
        string='Timesheet Sheet Lines',
        readonly=True,
        states={
            'new': [('readonly', False)],
            'draft': [('readonly', False)],
        },
    )
    new_line_ids = fields.One2many(
        comodel_name='hr_timesheet.sheet.new.analytic.line',
        inverse_name='sheet_id',
        string='Temporary Timesheets',
        readonly=True,
        states={
            'new': [('readonly', False)],
            'draft': [('readonly', False)],
        },
    )
    state = fields.Selection([
        ('new', 'New'),
        ('draft', 'Open'),
        ('confirm', 'Waiting Approval'),
        ('done', 'Approved')],
        default='new', track_visibility='onchange',
        string='Status', required=True, readonly=True, index=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        required=True,
        readonly=True,
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
    )
    add_line_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Select Project',
        help='If selected, the associated project is added '
             'to the timesheet sheet when clicked the button.',
    )
    add_line_task_id = fields.Many2one(
        comodel_name='project.task',
        string='Select Task',
        help='If selected, the associated task is added '
             'to the timesheet sheet when clicked the button.',
    )
    total_time = fields.Float(
        compute='_compute_total_time',
        store=True,
    )

    @api.multi
    @api.depends('date_start', 'date_end')
    def _compute_name(self):
        locale = self.env.context.get('lang') or self.env.user.lang or 'en_US'
        for sheet in self:
            if sheet.date_start == sheet.date_end:
                sheet.name = babel.dates.format_skeleton(
                    skeleton='MMMEd',
                    datetime=datetime.combine(sheet.date_start, time.min),
                    locale=locale,
                )
                continue

            period_start = sheet.date_start.strftime(
                '%V, %Y'
            )
            period_end = sheet.date_end.strftime(
                '%V, %Y'
            )

            if period_start == period_end:
                sheet.name = '%s %s' % (
                    _('Week'),
                    period_start,
                )
            else:
                sheet.name = '%s %s - %s' % (
                    _('Weeks'),
                    period_start,
                    period_end,
                )

    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_time(self):
        for sheet in self:
            sheet.total_time = sum(sheet.mapped('timesheet_ids.unit_amount'))

    @api.constrains('date_start', 'date_end')
    def _check_start_end_dates(self):
        for sheet in self:
            if sheet.date_start > sheet.date_end:
                raise ValidationError(
                    _('The start date cannot be later than the end date.'))

    @api.multi
    def _get_overlapping_sheet_domain(self, user_id=False):
        """ Hook for extensions """
        self.ensure_one()
        domain = [
            ('id', '!=', self.id),
            ('date_start', '<=', self.date_end),
            ('date_end', '>=', self.date_start),
            ('user_id', '=', user_id or self.user_id.id),
            ('company_id', '=', self._get_timesheet_sheet_company().id),
        ]
        return domain

    @api.constrains('date_start', 'date_end', 'employee_id')
    def _check_sheet_date(self, user_id=False):
        sheets = self if user_id else self.filtered('user_id')
        for sheet in sheets:
            domain = sheet._get_overlapping_sheet_domain(user_id=user_id)
            if self.search(domain, limit=1):
                raise ValidationError(
                    _('You cannot have 2 sheets that overlap!\n'
                        'Please use the menu \'Timesheet Sheet\' '
                        'to avoid this problem.'))

    @api.multi
    @api.constrains('company_id', 'employee_id')
    def _check_company_id_employee_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.employee_id.company_id and \
                    rec.company_id != rec.employee_id.company_id:
                raise ValidationError(
                    _('The Company in the Timesheet Sheet and in '
                      'the Employee must be the same.'))

    @api.multi
    @api.constrains('company_id', 'department_id')
    def _check_company_id_department_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.department_id.company_id and \
                    rec.company_id != rec.department_id.company_id:
                raise ValidationError(
                    _('The Company in the Timesheet Sheet and in '
                      'the Department must be the same.'))

    @api.multi
    @api.constrains('company_id', 'add_line_project_id')
    def _check_company_id_add_line_project_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.add_line_project_id.company_id and \
                    rec.company_id != rec.add_line_project_id.company_id:
                raise ValidationError(
                    _('The Company in the Timesheet Sheet and in '
                      'the Project must be the same.'))

    @api.multi
    @api.constrains('company_id', 'add_line_task_id')
    def _check_company_id_add_line_task_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.add_line_task_id.company_id and \
                    rec.company_id != rec.add_line_task_id.company_id:
                raise ValidationError(
                    _('The Company in the Timesheet Sheet and in '
                      'the Task must be the same.'))

    @api.multi
    def _get_timesheet_sheet_company(self):
        self.ensure_one()
        employee = self.employee_id
        company = employee.company_id or employee.department_id.company_id
        if not company:
            company = employee.user_id.company_id
        return company

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            company = self._get_timesheet_sheet_company()
            self.company_id = company
            self.department_id = self.employee_id.department_id

    @api.multi
    def _get_timesheet_sheet_lines_domain(self):
        self.ensure_one()
        domain = [
            ('date', '<=', self.date_end),
            ('date', '>=', self.date_start),
            ('employee_id', '=', self.employee_id.id),
            ('company_id', '=', self._get_timesheet_sheet_company().id),
            ('project_id', '!=', False),
        ]
        return domain

    @api.multi
    @api.depends('date_start', 'date_end')
    def _compute_line_ids(self):
        SheetLine = self.env['hr_timesheet.sheet.line']
        for sheet in self:
            if not all([sheet.date_start, sheet.date_end]):
                continue
            matrix = sheet._get_data_matrix()
            vals_list = []
            for key in sorted(matrix,
                              key=lambda key: self._get_matrix_sortby(key)):
                vals_list.append(sheet._get_default_sheet_line(matrix, key))
                sheet.clean_timesheets(matrix[key])
            sheet.line_ids = SheetLine.create(vals_list)

    @api.model
    def _matrix_key_attributes(self):
        """ Hook for extensions """
        return ['date', 'project_id', 'task_id']

    @api.model
    def _matrix_key(self):
        return namedtuple('MatrixKey', self._matrix_key_attributes())

    @api.model
    def _get_matrix_key_values_for_line(self, aal):
        """ Hook for extensions """
        return {
            'date': aal.date,
            'project_id': aal.project_id,
            'task_id': aal.task_id,
        }

    @api.model
    def _get_matrix_sortby(self, key):
        res = []
        for attribute in key:
            value = None
            if hasattr(attribute, 'name_get'):
                name = attribute.name_get()
                value = name[0][1] if name else ''
            else:
                value = attribute
            res.append(value)
        return res

    @api.multi
    def _get_data_matrix(self):
        self.ensure_one()
        MatrixKey = self._matrix_key()
        matrix = {}
        empty_line = self.env['account.analytic.line']
        for line in self.timesheet_ids:
            key = MatrixKey(**self._get_matrix_key_values_for_line(line))
            if key not in matrix:
                matrix[key] = empty_line
            matrix[key] += line
        for date in self._get_dates():
            for key in matrix.copy():
                key = MatrixKey(**{
                    **key._asdict(),
                    'date': date,
                })
                if key not in matrix:
                    matrix[key] = empty_line
        return matrix

    def _compute_timesheet_ids(self):
        AccountAnalyticLines = self.env['account.analytic.line']
        for sheet in self:
            domain = sheet._get_timesheet_sheet_lines_domain()
            timesheets = AccountAnalyticLines.search(domain)
            sheet.link_timesheets_to_sheet(timesheets)
            sheet.timesheet_ids = timesheets

    @api.onchange('date_start', 'date_end', 'employee_id')
    def _onchange_scope(self):
        self._compute_timesheet_ids()

    @api.onchange('date_start', 'date_end')
    def _onchange_dates(self):  # pragma: no cover
        if self.date_start > self.date_end:
            self.date_end = self.date_start

    @api.onchange('timesheet_ids')
    def _onchange_timesheets(self):
        self._compute_line_ids()

    @api.onchange('add_line_project_id')
    def onchange_add_project_id(self):
        """Load the project to the timesheet sheet"""
        if self.add_line_project_id:
            return {
                'domain': {
                    'add_line_task_id': [
                        ('project_id', '=', self.add_line_project_id.id),
                        ('company_id', '=', self.company_id.id),
                        ('id', 'not in',
                         self.timesheet_ids.mapped('task_id').ids)],
                },
            }
        else:
            return {
                'domain': {
                    'add_line_task_id': [('id', '=', False)],
                },
            }

    @api.model
    def _check_employee_user_link(self, vals):
        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if not employee.user_id:
                raise UserError(
                    _('In order to create a sheet for this employee, '
                      'you must link him/her to an user.'))
            return employee.user_id.id
        return False

    @api.multi
    def copy(self, default=None):
        if not self.env.context.get('allow_copy_timesheet'):
            raise UserError(_('You cannot duplicate a sheet.'))
        return super().copy(default=default)

    @api.model
    def create(self, vals):
        self._check_employee_user_link(vals)
        res = super().create(vals)
        res.write({'state': 'draft'})
        return res

    def _sheet_write(self, field, recs):
        self.with_context(sheet_write=True).write({field: [(6, 0, recs.ids)]})

    @api.multi
    def write(self, vals):
        new_user_id = self._check_employee_user_link(vals)
        if new_user_id:
            self._check_sheet_date(user_id=new_user_id)
        res = super().write(vals)
        for rec in self:
            if rec.state == 'draft' and \
                    not self.env.context.get('sheet_write'):
                rec._update_analytic_lines_from_new_lines(vals)
                if 'add_line_project_id' not in vals:
                    rec.delete_empty_lines(True)
        return res

    @api.multi
    def unlink(self):
        sheets = self.read(['state'])
        for sheet in sheets:
            if sheet['state'] in ('confirm', 'done'):
                raise UserError(
                    _('You cannot delete a timesheet sheet '
                      'which is already confirmed.'))
        return super().unlink()

    def _get_informables(self):
        """ Hook for extensions """
        self.ensure_one()
        return self.employee_id.parent_id.user_id.partner_id

    def _timesheet_subscribe_users(self):
        for sheet in self.sudo():
            subscribers = sheet._get_informables()
            if subscribers:
                self.message_subscribe(partner_ids=subscribers.ids)

    @api.multi
    def action_timesheet_draft(self):
        if self.filtered(lambda sheet: sheet.state != 'done'):
            raise UserError(_('Cannot revert to draft a non-approved sheet.'))
        if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            raise UserError(
                _('Only an HR Officer or Manager can refuse sheets '
                  'or reset them to draft.'))
        self.write({
            'state': 'draft',
        })

    @api.multi
    def action_timesheet_confirm(self):
        self._timesheet_subscribe_users()
        self.reset_add_line()
        self.write({'state': 'confirm'})

    @api.multi
    def action_timesheet_done(self):
        if self.filtered(lambda sheet: sheet.state != 'confirm'):
            raise UserError(_('Cannot approve a non-submitted sheet.'))
        if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            raise UserError(
                _('Only an HR Officer or Manager can approve sheets.'))
        self.write({
            'state': 'done',
        })

    @api.multi
    def action_timesheet_refuse(self):
        if self.filtered(lambda sheet: sheet.state != 'confirm'):
            raise UserError(_('Cannot reject a non-submitted sheet.'))
        self.write({
            'state': 'draft',
        })

    @api.multi
    def button_add_line(self):
        for rec in self:
            if rec.state in ['new', 'draft']:
                rec.add_line()
                rec.reset_add_line()

    def reset_add_line(self):
        self.write({
            'add_line_project_id': False,
            'add_line_task_id': False,
        })

    def _get_date_name(self, date):
        name = babel.dates.format_skeleton(
            skeleton='MMMEd',
            datetime=datetime.combine(date, time.min),
            locale=(
                self.env.context.get('lang') or self.env.user.lang or 'en_US'
            ),
        )
        name = re.sub(r'(\s*[^\w\d\s])\s+', r'\1\n', name)
        name = re.sub(r'([\w\d])\s([\w\d])', u'\\1\u00A0\\2', name)
        return name

    def _get_dates(self):
        start = self.date_start
        end = self.date_end
        if end < start:
            return []
        dates = [start]
        while start != end:
            start += relativedelta(days=1)
            dates.append(start)
        return dates

    @api.multi
    def _get_line_name(self, project_id, task_id=None, **kwargs):
        self.ensure_one()
        if task_id:
            return '%s - %s' % (project_id.name, task_id.name)

        return project_id.name

    @api.multi
    def _get_new_line_name_values(self):
        """ Hook for extensions """
        self.ensure_one()
        return {
            'project_id': self.add_line_project_id,
            'task_id': self.add_line_task_id,
        }

    @api.multi
    def _get_default_sheet_line(self, matrix, key):
        self.ensure_one()
        values = {
            'value_x': self._get_date_name(key.date),
            'value_y': self._get_line_name(**key._asdict()),
            'date': key.date,
            'project_id': key.project_id.id,
            'task_id': key.task_id.id,
            'unit_amount': sum(t.unit_amount for t in matrix[key]),
            'employee_id': self.employee_id.id,
            'company_id': self.company_id.id,
        }
        if self.id:
            values.update({'sheet_id': self.id})
        return values

    @api.model
    def _prepare_empty_analytic_line(self):
        return {
            'name': empty_name,
            'employee_id': self.employee_id.id,
            'date': self.date_start,
            'project_id': self.add_line_project_id.id,
            'task_id': self.add_line_task_id.id,
            'sheet_id': self.id,
            'unit_amount': 0.0,
            'company_id': self.company_id.id,
        }

    def add_line(self):
        if self.add_line_project_id:
            values = self._prepare_empty_analytic_line()
            name_line = self._get_line_name(
                **self._get_new_line_name_values()
            )
            name_list = list(set(self.line_ids.mapped('value_y')))
            if name_list:
                self.delete_empty_lines(False)
            if name_line not in name_list:
                self.timesheet_ids |= \
                    self.env['account.analytic.line'].create(values)

    def link_timesheets_to_sheet(self, timesheets):
        self.ensure_one()
        if self.id and self.state in ['new', 'draft']:
            for aal in timesheets.filtered(lambda a: not a.sheet_id):
                aal.write({'sheet_id': self.id})

    def clean_timesheets(self, timesheets):
        repeated = timesheets.filtered(lambda t: t.name == empty_name)
        if len(repeated) > 1 and self.id:
            return repeated.merge_timesheets()
        return timesheets

    @api.multi
    def _is_add_line(self, row):
        """ Hook for extensions """
        self.ensure_one()
        return self.add_line_project_id == row.project_id \
            and self.add_line_task_id == row.task_id

    @api.model
    def _is_line_of_row(self, aal, row):
        """ Hook for extensions """
        return aal.project_id.id == row.project_id.id \
            and aal.task_id.id == row.task_id.id

    def delete_empty_lines(self, delete_empty_rows=False):
        self.ensure_one()
        for name in list(set(self.line_ids.mapped('value_y'))):
            rows = self.line_ids.filtered(lambda l: l.value_y == name)
            if not rows:
                continue
            row = fields.first(rows)
            if delete_empty_rows and self._is_add_line(row):
                check = any([l.unit_amount for l in rows])
            else:
                check = not all([l.unit_amount for l in rows])
            if not check:
                continue
            row_lines = self.timesheet_ids.filtered(
                lambda aal: self._is_line_of_row(aal, row)
            )
            row_lines.filtered(
                lambda t: t.name == empty_name and not t.unit_amount
            ).unlink()
            if self.timesheet_ids != self.timesheet_ids.exists():
                self._sheet_write(
                    'timesheet_ids', self.timesheet_ids.exists())

    @api.multi
    def _update_analytic_lines_from_new_lines(self, vals):
        self.ensure_one()
        new_line_ids_list = []
        for line in vals.get('line_ids', []):
            # Every time we change a value in the grid a new line in line_ids
            # is created with the proposed changes, even though the line_ids
            # is a computed field. We capture the value of 'new_line_ids'
            # in the proposed dict before it disappears.
            # This field holds the ids of the transient records
            # of model 'hr_timesheet.sheet.new.analytic.line'.
            if line[0] == 1 and line[2] and line[2].get('new_line_id'):
                new_line_ids_list += [line[2].get('new_line_id')]
        for new_line in self.new_line_ids.exists():
            if new_line.id in new_line_ids_list:
                new_line._update_analytic_lines()
        self.new_line_ids.exists().unlink()
        self._sheet_write('new_line_ids', self.new_line_ids.exists())

    @api.model
    def _prepare_new_line(self, line):
        """ Hook for extensions """
        return {
            'sheet_id': line.sheet_id.id,
            'date': line.date,
            'project_id': line.project_id.id,
            'task_id': line.task_id.id,
            'unit_amount': line.unit_amount,
            'company_id': line.company_id.id,
            'employee_id': line.employee_id.id,
        }

    @api.multi
    def _is_compatible_new_line(self, line_a, line_b):
        """ Hook for extensions """
        self.ensure_one()
        return line_a.project_id.id == line_b.project_id.id \
            and line_a.task_id.id == line_b.task_id.id \
            and line_a.date == line_b.date

    @api.multi
    def add_new_line(self, line):
        self.ensure_one()
        new_line_model = self.env['hr_timesheet.sheet.new.analytic.line']
        new_line = self.new_line_ids.filtered(
            lambda l: self._is_compatible_new_line(l, line)
        )
        if new_line:
            new_line.write({'unit_amount': line.unit_amount})
        else:
            vals = self._prepare_new_line(line)
            new_line = new_line_model.create(vals)
        self._sheet_write('new_line_ids', self.new_line_ids | new_line)
        line.new_line_id = new_line.id

    # ------------------------------------------------
    # OpenChatter methods and notifications
    # ------------------------------------------------

    @api.multi
    def _track_subtype(self, init_values):
        if self:
            record = self[0]
            if 'state' in init_values and record.state == 'confirm':
                return 'hr_timesheet_sheet.mt_timesheet_confirmed'
            elif 'state' in init_values and record.state == 'done':
                return 'hr_timesheet_sheet.mt_timesheet_approved'
        return super()._track_subtype(init_values)


class AbstractSheetLine(models.AbstractModel):
    _name = 'hr_timesheet.sheet.line.abstract'
    _description = 'Abstract Timesheet Sheet Line'

    sheet_id = fields.Many2one(
        comodel_name='hr_timesheet.sheet',
        ondelete='cascade',
    )
    date = fields.Date()
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
    )
    unit_amount = fields.Float(
        string="Quantity",
        default=0.0,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
    )


class SheetLine(models.TransientModel):
    _name = 'hr_timesheet.sheet.line'
    _inherit = 'hr_timesheet.sheet.line.abstract'
    _description = 'Timesheet Sheet Line'

    value_x = fields.Char(
        string='Date Name',
    )
    value_y = fields.Char(
        string='Project Name',
    )
    new_line_id = fields.Integer(
        default=0,
    )

    @api.onchange('unit_amount')
    def onchange_unit_amount(self):
        """ This method is called when filling a cell of the matrix. """
        self.ensure_one()
        sheet = self._get_sheet()
        if not sheet:
            return {'warning': {
                'title': _("Warning"),
                'message': _("Save the Timesheet Sheet first."),
            }}
        sheet.add_new_line(self)

    @api.model
    def _get_sheet(self):
        sheet = self.sheet_id
        if not sheet:
            model = self.env.context.get('params', {}).get('model', '')
            obj_id = self.env.context.get('params', {}).get('id')
            if model == 'hr_timesheet.sheet' and isinstance(obj_id, int):
                sheet = self.env['hr_timesheet.sheet'].browse(obj_id)
        return sheet


class SheetNewAnalyticLine(models.TransientModel):
    _name = 'hr_timesheet.sheet.new.analytic.line'
    _inherit = 'hr_timesheet.sheet.line.abstract'
    _description = 'Timesheet Sheet New Analytic Line'

    @api.model
    def _is_similar_analytic_line(self, aal):
        """ Hook for extensions """
        return aal.date == self.date \
            and aal.project_id.id == self.project_id.id \
            and aal.task_id.id == self.task_id.id

    @api.model
    def _update_analytic_lines(self):
        sheet = self.sheet_id
        timesheets = sheet.timesheet_ids.filtered(
            lambda aal: self._is_similar_analytic_line(aal)
        )
        new_ts = timesheets.filtered(lambda t: t.name == empty_name)
        amount = sum(t.unit_amount for t in timesheets)
        diff_amount = self.unit_amount - amount
        if len(new_ts) > 1:
            new_ts = new_ts.merge_timesheets()
            sheet._sheet_write('timesheet_ids', sheet.timesheet_ids.exists())
        if not diff_amount:
            return
        if new_ts:
            unit_amount = new_ts.unit_amount + diff_amount
            if unit_amount:
                new_ts.write({'unit_amount': unit_amount})
            else:
                new_ts.unlink()
                sheet._sheet_write(
                    'timesheet_ids', sheet.timesheet_ids.exists())
        else:
            new_ts_values = sheet._prepare_new_line(self)
            new_ts_values.update({
                'name': empty_name,
                'unit_amount': diff_amount,
            })
            self.env['account.analytic.line'].create(new_ts_values)
