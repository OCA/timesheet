import {CalendarRenderer} from "@web/views/calendar/calendar_renderer";
import {TimesheetCalendarCommonRenderer} from "@hr_timesheet_calendar/views/timesheet_calendar/common/timesheet_calendar_common_renderer.esm";

export class TimesheetCalendarRenderer extends CalendarRenderer {}
TimesheetCalendarRenderer.components = {
    ...CalendarRenderer.components,
    day: TimesheetCalendarCommonRenderer,
    week: TimesheetCalendarCommonRenderer,
    month: TimesheetCalendarCommonRenderer,
};

TimesheetCalendarRenderer.props = {
    ...CalendarRenderer.props,
    copyRecord: {type: Function, optional: true},
};
