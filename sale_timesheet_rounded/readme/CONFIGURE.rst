Go to a project and set the following fields according to your needs:


* Timesheet rounding unit

Defines the rounding unit.
For instance, if you want to round to 1 hour, you can set `1.0`.
If you want to round to 15 min set `0.25`.


* Timesheet rounding method

Options: "No" (default), "Closest", "Up", "Down".

Please refer to `odoo.tools.float_utils.float_round` to understand the difference.


* Timesheet rounding factor (percentage)

When round unit is not defined you can round by a fixed %.


When using both a unit and a factor, the factor will be applied first:

  result = round(amount * percentage, unit)
