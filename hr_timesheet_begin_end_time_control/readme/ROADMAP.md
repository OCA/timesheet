- A line crossing midnight keeps empty begin/end hours; `hr_timesheet_begin_end`
  only supports begin and end on the same day.
- Time between begin and end that is not worked moves the end hour: the end
  hour is start + duration + `_get_begin_end_unworked_hours()`. The break of
  `hr_timesheet_begin_end_break` is supported out of the box; other modules
  can extend the method.
