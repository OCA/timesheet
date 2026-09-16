This module extends the standard timesheet approver rules so that a user with the
group *User: all timesheets* can also manage the timesheets of their subordinate
employees (i.e. employees whose *Manager* field points to the approver).

It updates the ``timesheet_line_rule_approver`` record rule to include the clause
``('employee_id.parent_id.user_id', 'in', (False, user.id))``.
