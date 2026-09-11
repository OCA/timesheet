If you want other default ranges different from weekly, you need to go:

- In the menu Configuration -\> Settings -\> **Timesheet Options**, and
  select in **Timesheet Sheet Range** the default range you want.
- When you have a weekly range you can also specify the **Week Start
  Day**.

To change who reviews submitted sheets, go to *Configuration \> Settings
\> Timesheet Options* and configure **Timesheet Sheet Review Policy**
accordingly.

For adding more review policies, look at the
*hr_timesheet_sheet_policy_xxx* extra modules.

To let specific users review an employee's sheets in addition to the
users allowed by the review policy, go to *Configuration \> Settings \>
Timesheet Options* and set **Timesheet Approver Field** to an employee
field pointing to one or more users. For every sheet, the users found in
that field on the employee are allowed to review it. Leave the setting
empty to rely on the review policy only.
