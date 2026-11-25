To use this module you need to:

1. Go to *Timesheets* and open or create a timesheet line (or the *Timesheets*
   tab of a project task).
2. Fill in the *Begin Hour* and *End Hour*.
3. Fill in the *Break* duration.
4. The *Duration* (worked hours) is automatically recomputed as the difference
   between end and begin hours, minus the break.

The line is validated so that the duration always equals
`End Hour - Begin Hour - Break`, that the begin hour precedes the end hour, and
that lines do not overlap for the same employee on the same day.
