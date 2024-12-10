This module adds a dashboard to manage timesheet and contractual hours.

General overview
================

The main purpose of this dashboard is to allow employee and manager to have an overview of their working time according to their contract.

Two dashboard will be needed to have to axes of analyse and will cover the timesheet time and the contractual time of the employee

Detailed requirements
=====================

Dashboard Hours report
----------------------

The hours report will allow to calculate the under or over hours of the employee at a day level. For this purpose we need to calculate the contractual hours the employee is requested to do for each day. The sum of the contractual hours, leaves and timesheet will give the time variation according to the contract.

The contractual hours should be calculated taking in account the following requirements:

- The calculation per day should take in account the contract valid at the date (for the future if there is no end date for the contract we use the current one)
- The working time per day will use the work plan (resource calendar) on the employee contract with the data per day and if not available the average per day (only the working days)
- Bank holiday should be excluded and they can come from the the calendar or the OCA module Public holiday (if installed)
- Number will be show in negative (in order that the final sum is negative if there is insufficient timesheet according to the contract time
- The timesheet section have the following requirement

 - The timesheet time will be aggregated at project level (and not task as on the timesheet app)
 - Working time and time off should be clearly separated (two columns)
 - Time off are taken only if fully validated and from the leave object and timesheet created from a leave should be ignored (in order to avoid duplicates)
 - By default we filter the current year until today and the user data.

Global requirement
------------------
The data coming from the timesheet and time off should always represent the situation we get if we go to the timesheet app or time off app (I mean by here that the data should be in real time). We accept that the data linked to the contract are updated every 24hours.

At the initialisation the system should be able to generate the past data.

Security
--------

The employee should not see the data from the others employee.
One exception for a manager that can see all the data from employees he is the manager of.

Pitfalls
========

- Limit cases about hours on weekend and hours worked at night inbetween 2 days.
