This module restores the behavior present in previous version (and restored
again in v13) of being able to reuse existing projects for generating the
tasks when confirming a sales order with service tracking.

When sale order is confirmed, product generating task can be added, but only
the first without adding a project to the sale order, avoiding the creation
of multiple projects.
