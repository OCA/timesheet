import {TimesheetCalendarController} from "@hr_timesheet_calendar/views/timesheet_calendar/timesheet_calendar_controller.esm";
import {TimesheetCalendarRenderer} from "@hr_timesheet_calendar/views/timesheet_calendar/timesheet_calendar_renderer.esm";
import {calendarView} from "@web/views/calendar/calendar_view";
import {registry} from "@web/core/registry";

export const timesheetCalendarView = {
    ...calendarView,
    Controller: TimesheetCalendarController,
    Renderer: TimesheetCalendarRenderer,
};
registry.category("views").add("timesheet_calendar", timesheetCalendarView);
