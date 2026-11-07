This module extends
[hr_timesheet_begin_end](https://github.com/OCA/timesheet/tree/19.0/hr_timesheet_begin_end)
by adding a **break duration** field to timesheet lines that use begin/end hours.

The worked time (`unit_amount`) is then computed as:

    Unit Amount = (End Hour - Begin Hour) - Break Duration

For example, a line starting at 08:00, ending at 16:30 with a 30 minute break
results in 8.00 worked hours.
