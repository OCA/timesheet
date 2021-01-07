[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/117/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-timesheet-117)
[![Build Status](https://travis-ci.com/OCA/timesheet.svg?branch=13.0)](https://travis-ci.com/OCA/timesheet)
[![codecov](https://codecov.io/gh/OCA/timesheet/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/timesheet)
[![Translation Status](https://translation.odoo-community.org/widgets/timesheet-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/timesheet-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Timesheet Management Modules

This project aim to deal with modules related to manage timesheet in a generic way

You'll find modules that:

  * Fulfill timesheet from holidays
  * Print Timesheet
  * Send reminder to employees
  * Integrate timesheet with project
  * ...

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[crm_timesheet](crm_timesheet/) | 13.0.1.0.0 | CRM Timesheet
[hr_timesheet_activity_begin_end](hr_timesheet_activity_begin_end/) | 13.0.1.0.1 | Timesheet Activities - Begin/End Hours
[hr_timesheet_analysis](hr_timesheet_analysis/) | 13.0.1.0.1 | Analyze tracked time in Pivot, Graph views
[hr_timesheet_sheet](hr_timesheet_sheet/) | 13.0.1.1.1 | Timesheet Sheets, Activities
[hr_timesheet_sheet_autodraft](hr_timesheet_sheet_autodraft/) | 13.0.1.0.0 | Automatically draft a Timesheet Sheet for every time entry that does not have a relevant Timesheet Sheet existing.
[hr_timesheet_sheet_autodraft_project](hr_timesheet_sheet_autodraft_project/) | 13.0.1.0.0 | Support per-project Timesheet Sheets auto-drafting.
[hr_timesheet_sheet_policy_project_manager](hr_timesheet_sheet_policy_project_manager/) | 13.0.1.0.0 | Allows setting Project Manager as Reviewer
[hr_timesheet_task_domain](hr_timesheet_task_domain/) | 13.0.1.0.0 | Limit task selection to tasks on currently-selected project
[hr_timesheet_task_required](hr_timesheet_task_required/) | 13.0.1.0.0 | Set task on timesheet as a mandatory field
[hr_timesheet_task_stage](hr_timesheet_task_stage/) | 13.0.1.1.0 | Open/Close task from corresponding Task Log entry
[hr_utilization_analysis](hr_utilization_analysis/) | 13.0.1.0.1 | View Utilization Analysis from Task Logs.
[sale_timesheet_order_line_sync](sale_timesheet_order_line_sync/) | 13.0.1.0.0 | Propagate task order line in not invoiced timesheet lines
[sale_timesheet_rounded](sale_timesheet_rounded/) | 13.0.1.0.0 | Round timesheet entries amount based on project settings.
[sale_timesheet_task_exclude](sale_timesheet_task_exclude/) | 13.0.1.0.0 | Exclude Task and related Timesheets from Sale Order

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
