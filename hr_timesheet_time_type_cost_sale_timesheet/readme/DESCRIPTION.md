This module connects `hr_timesheet_time_type_cost` and `sale_timesheet`.
Odoo installs it automatically when both modules are installed.

On a project with *Employee rate*, `sale_timesheet` gets the cost from the
`project.sale.line.employee.map` record.
`sale_timesheet` does not call `super()` on `_hourly_cost()`.
So the time type cost of `hr_timesheet_time_type_cost` does not operate.

This module gets the mapped cost and sends it to `_apply_time_type_cost()`.
So a ratio or a fixed hourly cost also operates on employee-rate projects.
`hr_timesheet_time_type_cost` operates on task-rate and project-rate projects.
This module does not change them.
