import {TimesheetCalendarController} from "@hr_timesheet_calendar/views/timesheet_calendar/timesheet_calendar_controller.esm";
import {TimesheetCalendarRenderer} from "@hr_timesheet_calendar/views/timesheet_calendar/timesheet_calendar_renderer.esm";
import {timesheetCalendarView as baseTimesheetCalendarView} from "@hr_timesheet/views/timesheet_calendar/timesheet_calendar_view";
import {registry} from "@web/core/registry";

export const timesheetCalendarView = {
    ...baseTimesheetCalendarView,
    Controller: TimesheetCalendarController,
    Renderer: TimesheetCalendarRenderer,
};

registry
    .category("views")
    .add("timesheet_calendar", timesheetCalendarView, {force: true});

registry
    .category("views")
    .add("timesheet_calendar_my_timesheets", timesheetCalendarView, {force: true});
