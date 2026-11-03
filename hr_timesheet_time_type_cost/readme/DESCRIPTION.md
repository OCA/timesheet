Odoo gives each timesheet hour the employee hourly cost.
In service work, the nature of the hour changes the cost of the project.
Examples are overtime, night work, weekend work and on-call duty.
The project profitability report must show this difference.

This module gives the cost rule to the time type:

| Time type (example) | `cost_type` | Value | Cost of one hour |
| --- | --- | --- | --- |
| Normal hours | `employee` | — | the employee hourly cost |
| Overtime | `ratio` | 1.5 | 1.5 × the employee hourly cost |
| Night shift | `ratio` | 1.25 | 1.25 × the employee hourly cost |
| On-call duty | `fixed` | 25.00 | 25.00 per hour, independent of the salary |

Set `cost_ratio` for a ratio and `fixed_cost` for a fixed amount.
The values in the table are examples.
A ratio follows a pay increase without a new configuration row.
A fixed amount gives the hours a contractual cost.
This cost does not come from the employee cost.

The module copies the rule to the line in two cases:
when the employee creates the line, and when the employee changes the time type.
So a change in the configuration of a time type affects new lines only.
The module does not change the analytic history.

Leave Company empty to share a time type between companies.
A shared time type accepts `employee` and `ratio`.
A fixed amount is money in the company currency.
So a fixed amount needs a company.

On a project with employee rate, `sale_timesheet` gets the cost from the
project and employee map.
`sale_timesheet` does not call `super()`.
The module `hr_timesheet_time_type_cost_sale_timesheet` installs automatically.
It applies the time type rule to the mapped cost.

The module does not cover:

- per-diems and allowances. These are expenses with an analytic distribution.
- payroll cost and overtime pay. This module gives an internal analytic rate.
- rates for one employee or one team.
- dated rate tables. The line keeps the rule that was valid at its creation.
- billing prices. These belong to `sale_timesheet`.
