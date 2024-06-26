Round timesheet lines amounts in sales based on project' settings.

A typical use case is: you work 5 minutes but you want to invoice 15
minutes.

With this module you can configure a rounding unit or factor on the
project and all the lines tracked on this project's tasks will show a
rounded amount.

If you want you can override the value manually on each entry.

The delivered quantity on the sale order line - and by consequence on
the invoice - will be computed using the rounded amount. Therefore,
expense lines and other non-timesheet lines will be updated with a
rounded amount that is equal to the amount.

WARNING: This module cannot be used with timesheet_grid without further
adapation as an update of an existing timesheet line will NOT update the
rounded amount. To achieve this, you need to override adjust_grid
function to pass the force_compute context key.
