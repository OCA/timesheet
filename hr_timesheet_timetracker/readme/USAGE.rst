The timetracking features of this module are pretty straightforward, while
rounding and editing of timetracked time deserves detailed explanation.

Rounding
~~~~~~~~

Rounding is performed on _timestamps_, not _duration_: e.g. if timetracking
was started at 09:02 AM and was stopped at 10:08 AM, Timesheet's Encoding Unit
is Hour and it's Rounding Precision of is configured as 0.1, Started-At
timestamp will be rounded from 09:02 AM to 09:00 AM and Stopped-At timestamp
will be rounded from 10:08 AM to 10:12 AM (with default rounding configration).
