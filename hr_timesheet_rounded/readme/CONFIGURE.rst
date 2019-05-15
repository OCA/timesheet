Go to a project and set the following fields according to your needs:


* Timesheet rounding granularity

Defines the rounding unit.
For instance, if you want to round to 1 hour, you can set `1.0`.
If you want to round to 15 min set `0.25`.


* Timesheet rounding method

Options: "Closest", "Up" (default).

Please refer to `odoo.tools.float_utils.float_round` to understand the difference.


* Timesheet invoicing factor in percentage

When granularity is not defined you can round by a fixed %.
