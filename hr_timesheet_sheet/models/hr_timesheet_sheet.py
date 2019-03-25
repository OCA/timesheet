# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018-2019 Brainbean Apps
# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import babel.dates
import logging
import re
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from dateutil.rrule import (MONTHLY, WEEKLY)

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
        }
    )
    line_ids = fields.One2many(
        comodel_name='hr_timesheet.sheet.line',
        compute='_compute_line_ids',
        string='Timesheet Sheet Lines',
        readonly=True,
        states={
            'new': [('readonly', False)],
            'draft': [('readonly', False)],
        }
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
        for sheet in self:
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

    @api.constrains('date_start', 'date_end', 'employee_id')
    def _check_sheet_date(self, forced_user_id=False):
        for sheet in self:
            new_user_id = forced_user_id or sheet.user_id.id
            if new_user_id:
                self.env.cr.execute(
                    """
                    SELECT id
                    FROM hr_timesheet_sheet
                    WHERE (date_start <= %s and %s <= date_end)
                        AND user_id=%s
                        AND company_id=%s
                        AND id <> %s""",
                    (sheet.date_end, sheet.date_start, new_user_id,
                     sheet.company_id.id, sheet.id))
                if any(self.env.cr.fetchall()):
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
            self.department_id = self.employee_id.department_id
            self.company_id = self._get_timesheet_sheet_company()

    def _get_timesheet_sheet_lines_domain(self):
        self.ensure_one()
        return [
            ('project_id', '!=', False),
            ('date', '<=', self.date_end),
            ('date', '>=', self.date_start),
            ('employee_id', '=', self.employee_id.id),
            ('company_id', '=', self._get_timesheet_sheet_company().id),
        ]

    @api.multi
    def _compute_line_ids(self):
        SheetLine = self.env['hr_timesheet.sheet.line']
        for sheet in self:
            if not all([sheet.date_start, sheet.date_end]):
                continue
            matrix = sheet._get_data_matrix()
            vals_list = []
            for item in sorted(matrix, key=lambda l: self._sort_matrix(l)):
                vals_list.append(sheet._get_default_sheet_line(matrix, item))
                sheet.clean_timesheets(matrix[item])
            sheet.line_ids = SheetLine.create(vals_list)

    def _sort_matrix(self, line):
        return [line[0], line[1].name, line[2].name or '']

    def _get_data_matrix(self):
        self.ensure_one()
        matrix = {}
        empty_line = self.env['account.analytic.line']
        for line in self.timesheet_ids:
            data_key = (line.date, line.project_id, line.task_id)
            if data_key not in matrix:
                matrix[data_key] = empty_line
            matrix[data_key] += line
        for date in self._get_dates():
            for item in matrix.copy():
                if (date, item[1], item[2]) not in matrix:
                    matrix[(date, item[1], item[2])] = empty_line
        return matrix

    @api.onchange('date_start', 'date_end', 'employee_id')
    def _onchange_dates(self):
        domain = self._get_timesheet_sheet_lines_domain()
        timesheets = self.env['account.analytic.line'].search(domain)
        self.link_timesheets_to_sheet(timesheets)
        self.timesheet_ids = timesheets

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

    @api.multi
    def copy(self, default=None):
        if not self.env.context.get('allow_copy_timesheet'):
            raise UserError(_('You cannot duplicate a sheet.'))
        return super().copy(default=default)

    @api.model
    def create(self, vals):
        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if not employee.user_id:
                raise UserError(
                    _('In order to create a sheet for this employee, '
                      'you must link him/her to an user.'))
        res = super().create(vals)
        res.write({'state': 'draft'})
        self.delete_empty_lines(True)
        return res

    @api.multi
    def write(self, vals):
        if 'employee_id' in vals:
            new_user_id = self.env['hr.employee'].\
                browse(vals['employee_id']).user_id.id
            if not new_user_id:
                raise UserError(
                    _('In order to create a sheet for this employee, '
                      'you must link him/her to an user.'))
            self._check_sheet_date(forced_user_id=new_user_id)
        res = super().write(vals)
        for rec in self:
            if rec.state == 'draft':
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
        analytic_timesheet_toremove = self.env['account.analytic.line']
        for sheet in self:
            analytic_timesheet_toremove += \
                sheet.timesheet_ids.filtered(lambda t: t.name == empty_name)
        analytic_timesheet_toremove.unlink()
        return super().unlink()

    def _timesheet_subscribe_users(self):
        for sheet in self.sudo():
            manager = sheet.employee_id.parent_id.user_id.partner_id
            if manager:
                self.message_subscribe(partner_ids=manager.ids)

    @api.multi
    def action_timesheet_draft(self):
        if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            raise UserError(
                _('Only an HR Officer or Manager can refuse sheets '
                  'or reset them to draft.'))
        self.write({'state': 'draft'})

    @api.multi
    def action_timesheet_confirm(self):
        self._timesheet_subscribe_users()
        self.reset_add_line()
        self.write({'state': 'confirm'})

    @api.multi
    def action_timesheet_done(self):
        if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            raise UserError(
                _('Only an HR Officer or Manager can approve sheets.'))
        if self.filtered(lambda sheet: sheet.state != 'confirm'):
            raise UserError(_("Cannot approve a non-submitted sheet."))
        self.write({'state': 'done'})

    @api.multi
    def action_timesheet_refuse(self):
        return self.action_timesheet_draft()

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
            locale=self.env.context.get('lang') or 'en_US',
        )
        name = re.sub(r'(\s*[^\w\d\s])\s+', r'\1\n', name)
        name = re.sub(r'([\w\d])\s([\w\d])', u'\\1\u00A0\\2', name)
        return name

    def _get_dates(self):
        start = self.date_start
        end = self.date_end
        if end < start:
            return []
        # time_period = end - start
        # number_of_days = time_period/timedelta(days=1)
        dates = [start]
        while start != end:
            start += relativedelta(days=1)
            dates.append(start)
        return dates

    def _get_line_name(self, project, task=None):
        if task:
            return '%s - %s' % (project.name, task.name)

        return project.name

    def _get_new_line_name(self):
        return self._get_line_name(
            self.add_line_project_id,
            self.add_line_task_id,
        )

    def _get_default_sheet_line(self, matrix, item):
        values = {
            'value_x': self._get_date_name(item[0]),
            'value_y': self._get_line_name(item[1], item[2]),
            'date': item[0],
            'project_id': item[1].id,
            'task_id': item[2].id,
            'unit_amount': sum(t.unit_amount for t in matrix[item]),
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
            name_line = self._get_new_line_name()
            if self.line_ids.mapped('value_y'):
                self.delete_empty_lines(False)
            if name_line not in self.line_ids.mapped('value_y'):
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

    def delete_empty_lines(self, delete_empty_rows=False):
        for name in self.line_ids.mapped('value_y'):
            row = self.line_ids.filtered(lambda l: l.value_y == name)
            if row:
                ts_row = self.timesheet_ids.filtered(
                    lambda x: x.project_id.id == row[0].project_id.id
                    and x.task_id.id == row[0].task_id.id
                )
                if delete_empty_rows and self.add_line_project_id:
                    check = any([l.unit_amount for l in row])
                else:
                    check = not all([l.unit_amount for l in row])
                if check:
                    ts_row.filtered(
                        lambda t: t.name == empty_name and not t.unit_amount
                    ).unlink()

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


class SheetLine(models.TransientModel):
    _name = 'hr_timesheet.sheet.line'
    _description = 'Timesheet Sheet Line'

    sheet_id = fields.Many2one(
        comodel_name='hr_timesheet.sheet',
        ondelete='cascade',
    )
    date = fields.Date(
        string='Date',
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
    )
    value_x = fields.Char(
        string='Date Name',
    )
    value_y = fields.Char(
        string='Project Name',
    )
    unit_amount = fields.Float(
        string="Quantity",
        default=0.0,
    )

    @api.onchange('unit_amount')
    def onchange_unit_amount(self):
        """This method is called when filling a cell of the matrix.
        It checks if there exists timesheets associated  to that cell.
        If yes, it does several comparisons to see if the unit_amount of
        the timesheets should be updated accordingly."""
        self.ensure_one()

        sheet = self.sheet_id
        if not sheet:
            model = self.env.context.get('params', {}).get('model', '')
            obj_id = self.env.context.get('params', {}).get('id')
            if model == 'hr_timesheet.sheet' and isinstance(obj_id, int):
                sheet = self.env['hr_timesheet.sheet'].browse(obj_id)
        if not sheet:
            return {'warning': {
                'title': _("Warning"),
                'message': _("Save the Timesheet Sheet first.")
            }}
        timesheets = sheet.timesheet_ids.filtered(
            lambda t: t.date == self.date
            and t.project_id.id == self.project_id.id
            and t.task_id.id == self.task_id.id
        )
        new_ts = timesheets.filtered(lambda t: t.name == empty_name)
        amount = sum(t.unit_amount for t in timesheets)
        diff_amount = self.unit_amount - amount
        if not diff_amount:
            return
        if new_ts:
            if len(new_ts) > 1:
                new_ts = new_ts.merge_timesheets()
            unit_amount = new_ts.unit_amount + diff_amount
            new_ts.write({'unit_amount': unit_amount})
        else:
            new_ts_values = self._line_to_timesheet(diff_amount)
            self.env['account.analytic.line'].create(new_ts_values)

    @api.model
    def _line_to_timesheet(self, amount):
        return {
            'name': empty_name,
            'employee_id': self.sheet_id.employee_id.id,
            'date': self.date,
            'project_id': self.project_id.id,
            'task_id': self.task_id.id,
            'sheet_id': self.sheet_id.id,
            'unit_amount': amount,
            'company_id': self.sheet_id.company_id.id,
        }
