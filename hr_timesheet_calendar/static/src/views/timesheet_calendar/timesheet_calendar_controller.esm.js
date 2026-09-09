import {CalendarController} from "@web/views/calendar/calendar_controller";
import {FormViewDialog} from "@web/views/view_dialogs/form_view_dialog";
import {_t} from "@web/core/l10n/translation";

export class TimesheetCalendarController extends CalendarController {
    get rendererProps() {
        const props = super.rendererProps;
        props.copyRecord = this.copyRecord.bind(this);
        return props;
    }

    getQuickCreateFormViewProps(record) {
        const props = super.getQuickCreateFormViewProps(record);
        const onDialogClosed = () => {
            this.model.load();
        };
        return {
            ...props,
            onRecordSaved: () => onDialogClosed(),
        };
    }

    async copyRecord(record, context = {}) {
        if (this.model.hasEditDialog) {
            let recordSaved = false;
            const lineId = await this.orm.call(
                this.model.resModel,
                "duplicate_today",
                [record.id],
                context
            );
            return new Promise((resolve, reject) => {
                context.default_values = record;
                const dialog = this.displayDialog(
                    FormViewDialog,
                    {
                        resModel: this.model.resModel,
                        resId: lineId,
                        context,
                        title: _t("New Timesheet Entry"),
                        viewId: this.model.formViewId,
                        onRecordSaved: () => {
                            recordSaved = true;
                            this.model.load();
                            resolve();
                        },
                    },
                    {
                        onClose: () => {
                            if (recordSaved === false) {
                                const unlinkContext = {...context};
                                delete unlinkContext.default_values;

                                this.orm
                                    .unlink(
                                        this.model.resModel,
                                        [lineId],
                                        unlinkContext
                                    )
                                    .then(() => {
                                        resolve();
                                        this.model.load();
                                    })
                                    .catch((error) => {
                                        this.logger.error("Unlink error:", error);
                                        reject(error);
                                    });
                            } else {
                                resolve();
                            }
                        },
                    }
                );
                this.dialog = dialog;
            });
        }
    }
}
