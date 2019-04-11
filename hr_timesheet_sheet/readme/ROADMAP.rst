* The timesheet grid is limited to display a max. of 1M cells, due to a
  limitation of the tree view limit parameter not being able to dynamically
  set a limit. Since default value of odoo, 40 records is too small, we decided
  to set 1M, which should be good enough in the majority of scenarios.
