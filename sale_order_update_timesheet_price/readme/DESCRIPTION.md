When a sale order line billed on delivered timesheets has been invoiced, Odoo forbids
modification of the unit price. When a price update is necessary, one can create a new
sale order or sale order line, but it is painful to link all projects, tasks, milestones
to the new order line.

This modules adds a button on already invoiced timesheet sale order lines to update the
unit price. It creates a new order line with the new price and re-links projects, tasks,
milestones and so line employee maps from the old line to the new line.
