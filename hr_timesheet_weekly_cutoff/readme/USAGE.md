If the cutoff day is configured as Monday:

- On Monday, users can still register timesheets for:
  - Monday
  - Sunday
  - Saturday
  - Friday
  - Thursday
  - Wednesday
  - Tuesday

- Starting Tuesday, users can no longer register
  timesheets dated Monday or earlier.

Users belonging to the group:

- Timesheet Weekly Cutoff Bypass

can register timesheets outside the weekly cutoff period.

Timesheets registered outside the allowed cutoff period
by bypass users are automatically marked as:

- Outside Weekly Cutoff

This flag can be used later for:

- reporting
- auditing
- filtering

## Technical Notes

The weekly cutoff restriction is enforced during both:

- record creation
- record update

This ensures compatibility with:

- editable tree views
- imports
- RPC calls
- automated processes

The restriction validation is applied per record to
ensure correct behavior during multi-record operations.
