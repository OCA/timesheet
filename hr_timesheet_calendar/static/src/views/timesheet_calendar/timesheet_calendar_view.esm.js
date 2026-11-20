import {TimesheetCalendarController} from "@hr_timesheet_calendar/views/timesheet_calendar/timesheet_calendar_controller.esm";
import {TimesheetCalendarRenderer} from "@hr_timesheet_calendar/views/timesheet_calendar/timesheet_calendar_renderer.esm";
import {registry} from "@web/core/registry";
import {timesheetCalendarMyTimesheetsView} from "@hr_timesheet/views/timesheet_calendar_my_timesheets/timesheet_calendar_my_timesheets_view";

export const timesheetCalendarView = {
    ...timesheetCalendarMyTimesheetsView,
    Controller: TimesheetCalendarController,
    Renderer: TimesheetCalendarRenderer,
};

registry.category("views").add("hr_timesheet_calendar", timesheetCalendarView);
