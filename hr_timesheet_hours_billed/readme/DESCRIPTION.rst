This module allows to specify billed amount of time in timesheet while still keeping original time tracked.
It might be useful if you want to invoice only part of the time logged in the timesheet.
It also implements „approval“ mechanism so only approved timesheets will be invoiced.

Additional field "Hours Billed" and "Approved" "Approved by" and "Approved on" are added to timesheet.
These  fields are visible only for "Timesheets: Administrator" group
"Hours Billed" field is used to compute Delivered Quantity in related Sale Order line.Only timesheets with "Approved" enabled are counted.

By default "Hours Bulled" field values are populated from the "Hours Spent" field of the timesheet.
