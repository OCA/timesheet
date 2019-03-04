from odoo import api, fields, models, _
from odoo.exceptions import UserError

import pytz


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    def _get_attendance_employee_tz(self, date=None):
        """Convert date according to timezone of user
        :param date: datetime.datetime.
        :return: datetime.date with applied timezone or False"""

        tz = False
        if self.employee_id.user_id:
            tz = self.employee_id.user_id.partner_id.tz
        if not date:
            return False
        time_zone = pytz.timezone(tz or 'UTC')
        attendance_tz_dt = pytz.UTC.localize(date)
        attendance_tz_dt = attendance_tz_dt.astimezone(time_zone)
        return attendance_tz_dt.date()

    def _get_timesheet_sheet(self):
        """Find and return current timesheet-sheet
        :return: recordset of hr_timesheet.sheet or False"""

        sheet_obj = self.env['hr_timesheet.sheet']
        check_in = False
        if self.check_in:
            check_in = self._get_attendance_employee_tz(date=self.check_in)

        domain = [('employee_id', '=', self.employee_id.id)]
        if check_in:
            domain += [
                ('date_start', '<=', check_in),
                ('date_end', '>=', check_in)
            ]

        sheet_ids = sheet_obj.search(domain, limit=1)
        return sheet_ids[:1] or False

    @api.depends('employee_id', 'check_in', 'check_out')
    def _compute_sheet_id(self):
        """Find and set current timesheet-sheet in
        current attendance record"""
        for attendance in self:
            attendance.sheet_id = attendance._get_timesheet_sheet()

    sheet_id = fields.Many2one(
        comodel_name='hr_timesheet.sheet',
        compute="_compute_sheet_id",
        string='Sheet',
        store=True)

    def _check_timesheet_state(self):
        """Check and raise error if current sheet not in draftstate"""
        if self._context.get('allow_modify_confirmed_sheet', False):
            return
        if self.sheet_id and self.sheet_id.state != 'draft':
            raise UserError(_(
                "You cannot modify an entry in a confirmed timesheet"
            ))

    @api.multi
    def unlink(self):
        # Restrict to delete attendance from confirmed timesheet-sheet
        for attendance in self:
            attendance._check_timesheet_state()

        return super(HrAttendance, self).unlink()

    @api.constrains('check_in', 'check_out')
    def _check_timesheet(self):
        """- Restrict to create attendance in confirmed timesheet-sheet
        - Restrict to add attendance date outside the current
        timesheet dates"""
        timesheet = self.sheet_id
        if not timesheet:
            return
        if timesheet and timesheet.state != 'draft':
            raise UserError(_(
                "You can not enter an attendance in a submitted timesheet. " +
                "Ask your manager to reset it before adding attendance."
            ))
        else:
            checkin_tz_date = self._get_attendance_employee_tz(
                date=self.check_in
            )
            checkout_tz_date = self._get_attendance_employee_tz(
                date=self.check_out
            )
            if ((timesheet.date_start > checkin_tz_date or
                 timesheet.date_end < checkin_tz_date) or
                    checkout_tz_date and (timesheet.date_start >
                                          checkout_tz_date or
                                          timesheet.date_end <
                                          checkout_tz_date)):
                raise UserError(_(
                    "You can not enter an attendance date " +
                    "outside the current timesheet dates."))
