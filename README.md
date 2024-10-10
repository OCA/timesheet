
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/timesheet&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/timesheet/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/timesheet/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/timesheet/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/timesheet/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/timesheet/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/timesheet)
[![Translation Status](https://translation.odoo-community.org/widgets/timesheet-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/timesheet-16-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# timesheet

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[crm_timesheet](crm_timesheet/) | 16.0.1.1.0 |  | CRM Timesheet
[hr_employee_cost_history](hr_employee_cost_history/) | 16.0.1.0.1 | [![edlopen](https://github.com/edlopen.png?size=30px)](https://github.com/edlopen) [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) | Adds an history to employee's costs.
[hr_timesheet_begin_end](hr_timesheet_begin_end/) | 16.0.1.0.1 |  | Timesheet - Begin/End Hours
[hr_timesheet_editable_top](hr_timesheet_editable_top/) | 16.0.1.0.0 |  | Add new timesheet entries to the top of the list
[hr_timesheet_employee_analytic_tag](hr_timesheet_employee_analytic_tag/) | 16.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Hr Timesheet Employee Analytic Tag
[hr_timesheet_name_customer](hr_timesheet_name_customer/) | 16.0.1.0.0 | [![solo4games](https://github.com/solo4games.png?size=30px)](https://github.com/solo4games) [![CetmixGitDrone](https://github.com/CetmixGitDrone.png?size=30px)](https://github.com/CetmixGitDrone) | Add ‘Description Customer’ field for timesheets
[hr_timesheet_report](hr_timesheet_report/) | 16.0.1.0.0 | [![alexey-pelykh](https://github.com/alexey-pelykh.png?size=30px)](https://github.com/alexey-pelykh) | Generate Timesheet Report from Task Logs
[hr_timesheet_sheet](hr_timesheet_sheet/) | 16.0.1.1.4 |  | Timesheet Sheets, Activities
[hr_timesheet_sheet_attendance](hr_timesheet_sheet_attendance/) | 16.0.1.0.0 |  | HR Timesheet Sheet Attendance
[hr_timesheet_sheet_autodraft](hr_timesheet_sheet_autodraft/) | 16.0.1.0.0 |  | Automatically draft a Timesheet Sheet for every time entry that does not have a relevant Timesheet Sheet existing.
[hr_timesheet_sheet_policy_department_manager](hr_timesheet_sheet_policy_department_manager/) | 16.0.1.0.0 | [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) [![edlopen](https://github.com/edlopen.png?size=30px)](https://github.com/edlopen) | Allows setting Department Manager as Reviewer
[hr_timesheet_sheet_policy_project_manager](hr_timesheet_sheet_policy_project_manager/) | 16.0.1.0.0 |  | Allows setting Project Manager as Reviewer
[hr_timesheet_task_domain](hr_timesheet_task_domain/) | 16.0.1.0.0 |  | Limit task selection to tasks on currently-selected project
[hr_timesheet_task_required](hr_timesheet_task_required/) | 16.0.1.0.0 |  | Set task on timesheet as a mandatory field
[hr_timesheet_task_stage](hr_timesheet_task_stage/) | 16.0.1.0.1 |  | Open/Close task from corresponding Task Log entry
[hr_timesheet_time_type](hr_timesheet_time_type/) | 16.0.1.0.0 |  | Ability to add time type in timesheet lines.
[project_task_analytic_propagation](project_task_analytic_propagation/) | 16.0.1.0.0 | [![edlopen](https://github.com/edlopen.png?size=30px)](https://github.com/edlopen) [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) | Updates timesheet's analytic account when their task changes the analytic.
[project_task_stage_allow_timesheet](project_task_stage_allow_timesheet/) | 16.0.1.0.0 |  | Allows to tell that a task stage is opened for timesheets.
[sale_timesheet_budget](sale_timesheet_budget/) | 16.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale timesheet budget
[sale_timesheet_invoice_link](sale_timesheet_invoice_link/) | 16.0.1.0.0 | [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) [![yajo](https://github.com/yajo.png?size=30px)](https://github.com/yajo) | Link invoices with timesheet lines
[sale_timesheet_line_exclude](sale_timesheet_line_exclude/) | 16.0.1.1.1 |  | Exclude Timesheet Line from Sale Order
[sale_timesheet_rounded](sale_timesheet_rounded/) | 16.0.1.0.0 |  | Round timesheet entries amount based on project settings.
[sale_timesheet_task_exclude](sale_timesheet_task_exclude/) | 16.0.1.0.0 |  | Exclude Task and related Timesheets from Sale Order
[sale_timesheet_timeline](sale_timesheet_timeline/) | 16.0.1.0.0 |  | Dates planning in sales order lines

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
