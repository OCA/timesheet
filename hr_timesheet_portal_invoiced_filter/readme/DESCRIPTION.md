This module extends the Odoo Timesheet Portal to introduce configurable visibility rules for timesheets.

It allows portal users to either see all timesheets or only invoiced timesheets in the portal. The visibility
can be configured at company level and overridden per partner via the partner form settings, with a default fallback
to the company configuration.

Additionally, it adjusts the display of the “Amount Due” section on tasks depending on the configured visibility
mode and the presence of uninvoiced timesheets.

Internal users are not affected by this filter.
