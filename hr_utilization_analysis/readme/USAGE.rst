To view analysis using Utilization Analysis Wizard:

#. Go to *Timesheets > Reporting > Utilization Analysis Wizard*.
#. Configure the data set and click "View".

To view analysis using Utilization Analysis Wizard on a specific set of Employees:

#. Go to *Employees > Employees*.
#. Select employees that should be used in the analysis
#. Press the *Action > View Utilization Analysis* button
#. Configure the data set and click "View".

To view analysis using Utilization Analysis Wizard on a specific set of Departments:

#. Go to *Employees > Departments*.
#. Select departments that should be used in the analysis
#. Press the *Action > View Utilization Analysis* button
#. Configure the data set and click "View".

With ``project_timesheet_holidays`` module installed, leaves are not taken into
account: for a single 4-hour entry on specific day with 8 working hours and
4 hours of leaves, capacity would be calculated as 8 hours and utilization
would be calculated as 100%.

Without ``project_timesheet_holidays`` module installed, leaves are taken into
account: for a single 4-hour entry on specific day with 8 working hours and
4 hours of leaves, capacity would be calculated as 4 hours and utilization
would be calculated as 100%.
