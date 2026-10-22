In order to create warning definitions for Timesheet Sheets, you need to
go:

- In the menu Configuration -\> **Warnings**, and start creating a new
  instance of a warning definition.
- Once inside, you will be able to specify the domain of the warning
  (the Timesheet Sheets it will be checked against) and the warning
  expression (the Python code that will be run and, if it evaluates to
  true, will indicate that a warning should be raised for that specific
  Sheet), amongst other fields.

To run those checks and raise the necessary warnings for a specific
Timesheet Sheet, you need to go:

- When looking at a Timesheet Sheet, go to the 'Warnings' tab.
- There you can press the button 'Generate Warnings', and you will be
  able to see the generated warnings in the list below the button.
- Warnings are also automatically generated when a Timesheet Sheet is
  submitted to the reviewer.
