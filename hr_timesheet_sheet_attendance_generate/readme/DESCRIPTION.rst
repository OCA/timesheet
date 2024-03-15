This module automates the creation of attendances based on the data in the
employee's timesheet sheets, ensuring consistency between recorded hours and
imputed timesheet hours for employees.

For each day in the timesheet sheet, one or more attendances will be created
if the day has imputed hours in the timesheet sheet but the employee does not
have any attendances in that same day.
The check in and check out times of the attendances, as well as the number of
generated attendances for each day, are retrieved from the employee's
established working hours or schedule.

Once the proposed attendances are created, the user can decide whether they
want them to be removed in the database or not (in case some of them are not
true or accurate, or for other reasons). The attendances will only be proposed
to users who have permissions to create attendances.
