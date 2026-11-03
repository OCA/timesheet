To use this module, you need to:

1. Go to *Timesheets / Timesheets / All Timesheets*.
1. Select the list view.
1. Click on the icon in the top-right corner and display the column *Invoice*.
1. Link the timesheet lines with the invoices you want from the same customer.

Additionally, when you open an invoice that has timesheets linked to its sale
order lines but not yet linked to the invoice itself, a warning alert will
appear at the top of the invoice form. From there you can:

- Click **Link All** to automatically link all pending timesheets to this
  invoice.
- Click **Select Manually** to open a filtered list of pending timesheets where
  you can select specific ones and click **Link to Invoice**.
- Click **Dismiss** to hide the alert for this invoice.

Once a timesheet is linked to an invoice that is not cancelled, Odoo considers it
invoiced, so its duration, date, employee, project, task, sale order item and
partner can no longer be modified. To edit it, unlink it first (empty its
*Invoice* column) or cancel the invoice.
