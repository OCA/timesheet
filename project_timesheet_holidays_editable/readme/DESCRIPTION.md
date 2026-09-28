By default, every timesheet generated from a leave becomes read-only, so nobody can directly edit it and e.g. change its hour count. This shouldn't occur in Odoo previous versions.

This could be annoying, because for certain leaves (like medical leaves), final spent time should be different than initial leave filled. This forces to reject, modify and then approve again leave. Exact time could not be filled sometimes anyway, due to leave form hour selection.

This addon re-enables timesheet edition when they're generated from leaves (initially name and quant fields), letting us make it editable depending on leave type.
