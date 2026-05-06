This module addresses the need to control which users can view cost information
in timesheet reports. In many organizations, regular employees should be able to
see time tracking information but not the monetary costs associated with that time.

The module leverages the `group_allow_read_analytic_amount` group from the
[`analytic_amount_security`](https://github.com/OCA/account-analytic/tree/18.0/analytic_amount_security)
module to restrict access to:

- Amount field in Timesheets Analysis Report
- Cost fields in Timesheet Attendance Report (timesheets_cost, attendance_cost,
  cost_difference)

This allows for fine-grained control over financial data visibility while
maintaining transparency for time tracking.
