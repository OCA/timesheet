import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {TimesheetCalendarCommonPopover} from "@hr_timesheet_calendar/views/timesheet_calendar/common/timesheet_calendar_common_popover.esm";

export class TimesheetCalendarCommonRenderer extends CalendarCommonRenderer {
    getPopoverProps() {
        const result = super.getPopoverProps(...arguments);
        result.copyRecord = this.props.copyRecord;

        return result;
    }
}
TimesheetCalendarCommonRenderer.components = {
    ...CalendarCommonRenderer.components,
    Popover: TimesheetCalendarCommonPopover,
};

TimesheetCalendarCommonRenderer.props = {
    ...CalendarCommonRenderer.props,
    copyRecord: {type: Function, optional: true},
};
