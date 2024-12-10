# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def get_time_quantities(self, date=None):
        """Process each attendance by summing morning and afternoon hours
        and defining day percentage correspondingly (0.5 if only morning,
        1.0 if both).

        By default, hours_per_day from calendar is returned and 1 full day.

        :param date: filter attendances week day with this date
        :return: a dict as follow: {
            "hours_qty": .0,
            "days_qty": .0;
        }
        """
        self.ensure_one()
        hours_qty = days_qty = 0.0
        attendances = self.attendance_ids
        if date:
            attendances = attendances.filtered(
                lambda att: int(att.dayofweek) == date.weekday()
            )
        for attendance in attendances:
            hours_qty += attendance.hour_to - attendance.hour_from
            if attendance.day_period in ("morning", "afternoon"):
                days_qty += 0.5
        return {
            "hours_qty": hours_qty or self.hours_per_day,
            "days_qty": days_qty or 1.0,
        }
