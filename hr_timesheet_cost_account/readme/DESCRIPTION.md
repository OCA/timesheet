This module allows recognizing timesheet-based labor costs in accounting.

It introduces a **Timesheet Costing** document that collects timesheet lines
within a selected date range (optionally filtered by project and/or employee),
computes the total cost based on each employee's hourly cost, and generates
a journal entry with:

- **Debit** to the cost account for each timesheet line (including analytic distribution)
- **Credit** to the suspense account for the total amount