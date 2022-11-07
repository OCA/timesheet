# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time

from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, WEEKLY
from pytz import UTC, timezone

from odoo import fields, models


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    def _get_subscribers(self):
        """Reviewers are going to be notified using activities"""
        res = super()._get_subscribers()
        res = res - self._get_possible_reviewers().mapped("partner_id")
        return res

    def write(self, vals):
        res = super().write(vals)

        for sheet in self.filtered(lambda sheet: sheet.state == "draft"):
            # NOTE: user_id is written manually instead of using new_user_id
            # in order to update only activities with different user_id
            activities = sheet.activity_reschedule(
                ["hr_timesheet_sheet_activity.activity_sheet_resubmission"],
            )
            for activity in activities:
                if activity.user_id == sheet.user_id:
                    continue
                if activity.user_id != self.env.user:
                    # NOTE: Only assigned user can update the activity
                    activity = activity.sudo()
                activity.write(
                    {
                        "user_id": sheet.user_id.id,
                    }
                )
            if activities:
                continue

            deadline = sheet._activity_sheet_submission_deadline()

            # NOTE: Instead of updating activities using activity_reschedule,
            # manually update only needed fields
            activities = sheet.activity_reschedule(
                ["hr_timesheet_sheet_activity.activity_sheet_submission"],
            )
            for activity in activities:
                values = {}
                if activity.user_id != sheet.user_id:
                    values.update(
                        {
                            "user_id": sheet.user_id.id,
                        }
                    )
                if activity.date_deadline != deadline:
                    values.update(
                        {
                            # NOTE: user_id is set to trigger a notification
                            "user_id": sheet.user_id.id,
                            "date_deadline": deadline,
                        }
                    )
                if not values:
                    continue

                if activity.user_id != self.env.user:
                    # NOTE: Only assigned user can update the activity
                    activity = activity.sudo()

                # NOTE: to get consistent results, disable automatic notice
                # and send one manually
                activity.with_context(
                    mail_activity_quick_update=True,
                ).write(values)
                activity.action_notify()
            if activities:
                continue

            sheet.activity_schedule(
                "hr_timesheet_sheet_activity.activity_sheet_submission",
                date_deadline=deadline,
                user_id=sheet.user_id.id,
            )

        return res

    def action_timesheet_draft(self):
        for sheet in self:
            sheet.activity_schedule(
                "hr_timesheet_sheet_activity.activity_sheet_resubmission",
                date_deadline=sheet._activity_sheet_resubmission_deadline(),
                user_id=sheet.user_id.id,
            )

        super().action_timesheet_draft()

    def action_timesheet_confirm(self):
        super().action_timesheet_confirm()

        # NOTE: activity_reschedule is used instead of activity_feedback
        # to accomodate non-assigned-user completion
        activities = self.activity_reschedule(
            [
                "hr_timesheet_sheet_activity.activity_sheet_submission",
                "hr_timesheet_sheet_activity.activity_sheet_resubmission",
            ]
        )
        for activity in activities:
            if activity.user_id != self.env.user:
                # NOTE: Only assigned user can update the activity
                activity = activity.sudo()
            activity.action_feedback()

        for sheet in self:
            for reviewer in sheet._get_possible_reviewers():
                deadline = sheet._activity_sheet_review_deadline(reviewer)
                sheet.activity_schedule(
                    "hr_timesheet_sheet_activity.activity_sheet_review",
                    date_deadline=deadline,
                    user_id=reviewer.id,
                )

    def action_timesheet_done(self):
        super().action_timesheet_done()

        # NOTE: activity_reschedule is used instead of activity_feedback
        # to accomodate non-assigned-user completion
        activities = self.activity_reschedule(
            [
                "hr_timesheet_sheet_activity.activity_sheet_review",
            ]
        )
        for activity in activities:
            if activity.user_id != self.env.user:
                # NOTE: Only assigned user can update the activity
                activity = activity.sudo()
            activity.action_feedback()

    def action_timesheet_refuse(self):
        for sheet in self:
            sheet.activity_schedule(
                "hr_timesheet_sheet_activity.activity_sheet_resubmission",
                date_deadline=sheet._activity_sheet_resubmission_deadline(),
                user_id=sheet.user_id.id,
            )

        super().action_timesheet_refuse()

        # NOTE: activity_reschedule is used instead of activity_feedback
        # to accomodate non-assigned-user completion
        activities = self.activity_reschedule(
            [
                "hr_timesheet_sheet_activity.activity_sheet_review",
            ]
        )
        for activity in activities:
            if activity.user_id != self.env.user:
                # NOTE: Only assigned user can update the activity
                activity = activity.sudo()
            activity.action_feedback()

    def _activity_sheet_submission_deadline(self):
        """Hook for extensions"""
        self.ensure_one()

        employee_timezone = timezone(self.employee_id.tz or "UTC")
        employee_today = self.env.context.get(
            "hr_timesheet_sheet_activity_today",
            fields.Datetime.now()
            .replace(tzinfo=UTC)
            .astimezone(employee_timezone)
            .date(),
        )

        # Get last workday of employee or last day of period (in user tz)
        datetime_start = datetime.combine(
            self.date_start,
            time.min,
        ).replace(tzinfo=employee_timezone)
        datetime_end = datetime.combine(
            max(self.date_end, employee_today), time.max
        ).replace(tzinfo=employee_timezone)
        worktimes = self.employee_id.list_work_time_per_day(
            datetime_start,
            datetime_end,
        )
        worktimes = list(filter(lambda worktime: worktime[1] > 0, worktimes))
        if worktimes:
            return worktimes[-1][0]  # Last workday of period
        return datetime_end.date()

    def _activity_sheet_resubmission_deadline(self):
        """Hook for extensions"""
        self.ensure_one()
        return None

    def _activity_sheet_review_deadline(self, reviewer):
        """Hook for extensions"""
        self.ensure_one()

        employee_timezone = timezone(self.employee_id.tz or "UTC")
        employee_today = self.env.context.get(
            "hr_timesheet_sheet_activity_today",
            fields.Datetime.now()
            .replace(tzinfo=UTC)
            .astimezone(employee_timezone)
            .date(),
        )
        deadline = max(self.date_end + relativedelta(days=1), employee_today)

        reviewer_employee = (
            self.env["hr.employee"]
            .with_context(
                active_test=False,
            )
            .search(
                [("user_id", "=", reviewer.id)],
                limit=1,
            )
        )
        if not reviewer_employee:
            return deadline

        worktimes = reviewer_employee.list_work_time_per_day(
            datetime.combine(deadline, time.min).replace(tzinfo=employee_timezone),
            datetime.combine(
                deadline + self._activity_sheet_review_max_period(), time.max
            ).replace(tzinfo=employee_timezone),
        )
        worktimes = list(filter(lambda worktime: worktime[1] > 0, worktimes))
        if worktimes:
            return worktimes[0][0]  # First workday of period
        return (
            datetime.combine(deadline, time.max)
            .replace(tzinfo=employee_timezone)
            .astimezone(timezone(reviewer_employee.tz or "UTC"))
            .date()
        )

    def _activity_sheet_review_max_period(self):
        """Hook for extensions"""
        self.ensure_one()
        sheet_range = self.company_id.sheet_range
        if not sheet_range:
            r = WEEKLY
        elif sheet_range == "DAILY":
            r = 1
        elif sheet_range == "WEEKLY":
            r = 2
        elif sheet_range == "MONTHLY":
            r = 3
        if r == WEEKLY:
            return relativedelta(weeks=1)
        elif r == MONTHLY:
            return relativedelta(months=1)
        return relativedelta(days=1)
