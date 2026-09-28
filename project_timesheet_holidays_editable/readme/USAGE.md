Once installed, it adds a configuration option to define the editability level of timesheets generated from time off requests at the company level.

Configuration

After installing the module, follow these steps:

1. Go to Settings (or navigate to Configuration → Settings within the Timesheets or Time Off apps).
2. Locate the Time Off section (where timesheet generation for leaves is configured).
3. Make sure an Internal Project (`internal_project_id`) is set. (The editability configuration menu is only visible if a global internal project is defined for the company).
4. Configure the Timesheet Edit Level.

Timesheet Restriction Levels

You can define how restrictive the generated timesheets are for the company:

1. None
    - The generated timesheet entries cannot be edited by anyone

2. Officer
    - Timesheet entries can only be edited by users belonging to the group: hr_holidays.group_hr_holidays_user
    - Prevents regular employees from modifying generated timesheets

3. All
    - Timesheet entries can be edited by any user with access to timesheets
