This module allows to set which Sale order item to use for new timesheets in a specific task, without updating the related Sale order item for all the existing timesheets in that task. This value can be set in field "Default sale order item" in the task itself.

In project > invoicing, updating field "Default Sales Order Item" updates new field "Default sale order item" in all tasks.

It also allows to select in both project and tasks a Sale order item from a different SO than the one set in project configuration.

Use case:

A new "timesheet hours" line is added to SO related to project (or to a new SO for same customer), but hours on the previous SO line have not all been billed yet.

This module allows to add new timesheet lines related to the new SO item, while keeping the previously inputted hours related to the previous SO item.
