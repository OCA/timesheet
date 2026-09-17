import {CalendarCommonPopover} from "@web/views/calendar/calendar_common/calendar_common_popover";

export class TimesheetCalendarCommonPopover extends CalendarCommonPopover {
    onCopyEvent() {
        this.props.copyRecord(this.props.record);
        this.props.close();
    }
}

TimesheetCalendarCommonPopover.subTemplates = {
    ...CalendarCommonPopover.subTemplates,
    body: "timesheet.TimesheetCalendarCommonPopover.body",
    footer: "timesheet.TimesheetCalendarCommonPopover.footer",
};

TimesheetCalendarCommonPopover.props = {
    ...CalendarCommonPopover.props,
    copyRecord: Function,
};
