Once installed, it adds a configuration option to define the editability level of timesheets generated from each Time Off Type.

Configuration

After installing the module, follow these steps:

1. Go to Time Off (hr_holidays)
2. Navigate to Configuration → Time Off Types
3. Select the desired Time Off Type
4. Make sure the option “Generate Timesheets” (timesheet_generate) is enabled (This configuration menu is only visible if timesheet generation is enabled).
5. Configure the Timesheet Restriction Level

Timesheet Restriction Levels

Each Time Off Type can define how restrictive the generated timesheets are:

1. None

    - The generated timesheet entries cannot be edited by anyone

2. Officer

    - Timesheet entries can only be edited by users belonging to the group: hr_holidays.group_hr_holidays_user
    - Prevents regular employees from modifying generated timesheets

3. All

    - Timesheet entries can be edited by any user with access to timesheets