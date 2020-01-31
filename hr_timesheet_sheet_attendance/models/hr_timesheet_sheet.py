from odoo import api, fields, models, _
from datetime import datetime, timedelta, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    def _compute_attendance_count(self):
        '''Compute total number of attendance records
        linked to current timesheet'''

        for attendances in self:
            attendances.attendance_count = len(attendances.attendances_ids)

    @api.depends('timesheet_ids', 'timesheet_ids.unit_amount',
                 'attendances_ids', 'attendances_ids.check_in',
                 'attendances_ids.check_out', 'attendances_ids.employee_id')
    def _compute_attendance_time(self):
        '''Compute total attendance time and
        difference in total attendance-time
        and timesheet-entry '''

        current_date = datetime.now()
        for sheet in self:
            atte_without_checkout = sheet.attendances_ids.filtered(
                lambda attendance: not attendance.check_out)
            atte_with_checkout = sheet.attendances_ids - atte_without_checkout
            total_time = sum(atte_with_checkout.mapped('worked_hours'))
            for attendance in atte_without_checkout:
                delta = current_date - datetime.strptime(
                    attendance.check_in,
                    DEFAULT_SERVER_DATETIME_FORMAT)
                total_time += delta.total_seconds() / 3600.0
            sheet.total_attendance = total_time

            # calculate total difference
            total_working_time = sum(sheet.mapped('timesheet_ids.unit_amount'))
            sheet.total_difference = total_time - total_working_time

    total_attendance = fields.Float(
        compute='_compute_attendance_time',
        string='Total Attendance',
    )
    total_difference = fields.Float(
        compute='_compute_attendance_time',
        string='Difference',
    )
    attendances_ids = fields.One2many(
        comodel_name='hr.attendance',
        inverse_name='sheet_id',
        string='Attendances')
    attendance_state = fields.Selection(
        related='employee_id.attendance_state',
        string='Current Status')
    attendance_count = fields.Integer(
        compute='_compute_attendance_count',
        string="Attendance Count")

    @api.multi
    def attendance_action_change(self):
        '''Call attendance_action_change to
        perform Check In/Check Out action
        Returns last attendance record'''

        return self.employee_id.attendance_action_change()

    @api.multi
    def action_timesheet_confirm(self):
        self.check_employee_attendance_state()
        return super(HrTimesheetSheet, self).action_timesheet_confirm()

    def check_employee_attendance_state(self):
        """Restrict to submit sheet contains
        attendance without checkout"""
        for sheet in self:
            ids_not_checkout = sheet.attendances_ids.filtered(
                lambda att: att.check_in and not att.check_out)
            if not ids_not_checkout:
                continue
            raise UserError(_(
                "The timesheet cannot be validated as it does " +
                "not contain an equal number of sign ins and sign outs."))

    @api.multi
    def get_attendance_by_day(self):
        self.ensure_one()
        result = []
        date_end = fields.Date.from_string(self.date_end)
        date_start = fields.Date.from_string(self.date_start)
        date_range = (date_end - date_start).days
        result = [0] * (date_range + 1)
        for attendance in self.attendances_ids:
            checkin_date = fields.Date.from_string(attendance.check_in)
            checkout_date = fields.Date.from_string(attendance.check_out)
            if checkin_date == checkout_date:
                delta = (checkin_date - date_start).days
                result[delta] += attendance.worked_hours
            else:
                attendance_range = (checkout_date - checkin_date).days
                curr_date = datetime.combine(checkin_date, time())
                for delta in range(0, attendance_range + 1):
                    if curr_date == datetime.combine(checkin_date, time()):
                        start_time = fields.Datetime.from_string(
                            attendance.check_in
                        )
                    else:
                        start_time = curr_date
                    if curr_date == datetime.combine(checkout_date, time()):
                        end_time = fields.Datetime.from_string(
                            attendance.check_out
                        )
                    else:
                        end_time = curr_date + timedelta(days=1)
                    work_time = \
                        (end_time - start_time).total_seconds() / 3600.0
                    result[delta] += work_time
                    curr_date = end_time
        return result

    @api.model
    def create(self, vals):
        res = super(HrTimesheetSheet, self).create(vals)
        attendances = self.env['hr.attendance'].search([
            ('sheet_id', '=', False),
            ('check_in', '>=', res.date_start),
            ('check_in', '<=', res.date_end),
            '|',
            ('check_out', '=', False),
            '&',
            ('check_out', '>=', res.date_start),
            ('check_out', '<=', res.date_end),
        ])
        attendances._compute_sheet_id()
        return res
