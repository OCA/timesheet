This module evaluates a set of quality requirements related to Timesheet Sheets.
For each sheet, using its employee's calendar plannings
(and their associated working time specifications) it computes the theoretical
working time for each day in the sheet and compares it with the real working time,
present in the actual sheet.

The requirements it evaluates are:

* Invalid hours per day: The employee's imputed hours for one or more days
  deviate from the theoretical hours for those specific days.
* Invalid hours per week: The employee's imputed hours for an entire week
  differ from the theoretical hours for that week.
* Hours on non working day: Flags situations where employees have
  recorded hours on a day designated as a non-working day.

The requirements are later available in the class as boolean fields.
With this information, Timesheet Sheets submitters and reviewers can have a better
idea about the consistency of the imputed work hours with the calendar that they should adhere to.
