When a time off request is validated, or a public holiday is created, Odoo
books a timesheet entry on the internal project for every working day off,
carrying just the hours of that day. With `hr_timesheet_time_control` such an
entry also gets a start and end time, and as nothing sets them they end up
being the time of day the entry was generated.

This module starts these generated entries with the working hours of the
employee: the entry begins with the first attendance of the day that falls
in the time off and lasts the hours of the day. A morning or full day off
starts with the morning, an afternoon off with the afternoon. As breaks are
not counted, the entry ends before the working hours do.
