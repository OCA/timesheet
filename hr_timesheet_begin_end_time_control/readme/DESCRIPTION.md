Glue between `hr_timesheet_begin_end` and `hr_timesheet_time_control`.

The timer of `hr_timesheet_time_control` records a start and end time
(`Start Time` / `End Time`), while `hr_timesheet_begin_end` adds its own
`Begin Hour` / `End Hour`. Without this module the two never meet: a stopped
timer leaves Begin Hour and End Hour empty.

This module keeps them in sync:

- Stopping a timer (Stop button, or starting a new timer which stops the
  running one) fills Begin Hour and End Hour in the employee's time zone.
- Changing the Start Time or the duration of such a line moves Begin Hour and
  End Hour along.
- Changing Begin Hour moves the Start Time to that hour on the line's date.

Lines that cannot be expressed as a begin/end hour on one day (a timer running
past midnight) or whose hours would overlap another line of the same employee
keep empty begin/end hours, so stopping the timer never fails.
