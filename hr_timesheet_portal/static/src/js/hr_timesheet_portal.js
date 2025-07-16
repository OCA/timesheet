/** @odoo-module */

import publicWidget from '@web/legacy/js/public/public_widget';
import {_t} from '@web/core/l10n/translation';
import {session} from "@web/session";
import {user} from "@web/core/user";

export const HrTimesheetPortal = publicWidget.Widget.extend({
    selector: "div.hr_timesheet_portal",
    events: {
        "click h5": "_onclick_add",
        "click tr[data-line-id]:not(.edit)": "_onclick_edit",
        "click i.fa-trash": "_onclick_delete",
        "click button.submit": "_onclick_submit",
        "submit form": "_onclick_submit",
        "click button.cancel": "_reload_timesheet",
    },

    /**
     * @override
     */
    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
        this.ui = this.bindService("ui");
    },

    /**
    * @override
    */
    start: function (editable_mode) {
        if (editable_mode) {
            this.stop();
        }
    },

    _onclick_delete: async function (e) {
        e.stopPropagation();
        this.ui.block();
        let line = jQuery(e.currentTarget).parents("tr").data("line-id");
        await this.orm.unlink("account.analytic.line", [line])
            .then(this.proxy("_reload_timesheet"))
            .catch(this.proxy("_display_failure"))
            .finally(() => {
                this.ui.unblock();
            });
    },

    _onclick_add: async function () {
        let self = this;
        let uid = Array.isArray(session.user_id) ? session.user_id[0] : user.userId;
        let account = this.$el.data("account-id");
        let project = this.$el.data("project-id");
        let task = this.$el.data("task-id");

        this.ui.block();
        await this.orm.call("account.analytic.line", "create", [
            [
                {
                    user_id: uid,
                    account_id: account,
                    project_id: project,
                    task_id: task,
                    unit_amount: 0,
                    name: "/",
                },
            ],
        ]).then(function (line_id) {
            return self._reload_timesheet().then(function () {
                setTimeout(self._edit_line.bind(self, line_id), 0);
            });
        }).catch(this.proxy("_display_failure"))
            .finally(() => {
                this.ui.unblock();
            });
    },

    _onclick_edit: function (e) {
        return this._edit_line(jQuery(e.target).parents("tr").data("line-id"));
    },

    _onclick_submit: async function (e) {
        e.preventDefault();
        this.ui.block();
        let $tr = jQuery(e.target).parents("tr"),
            data = Object.fromEntries(
                $tr.find("form").serializeArray().map(field => [field.name, field.value])
            );
        await this.orm.write("account.analytic.line", [$tr.data("line-id")], data)
            .then(this.proxy("_reload_timesheet"))
            .catch(this.proxy("_display_failure"))
            .finally(() => {
                this.ui.unblock();
            });
    },

    _reload_timesheet: function () {
        let self = this;
        this.$el.children("div.alert").remove();
        return $.ajax({
            dataType: "html",
        }).then(function (data) {
            let timesheets = jQuery.parseHTML(data).filter(function (element) {
                    let dhtp = jQuery(element).find("div.hr_timesheet_portal")
                    return dhtp.length > 0;
                }),
                $tbody = jQuery(timesheets).find("tbody");

            const $tableTimesheet = $('.hr_timesheet_portal .o_portal_my_doc_table');
            const $tableSubtotal = $('.hr_timesheet_portal .container_subtotal table');
            $tableTimesheet.find("tbody").remove();
            $tableSubtotal.find("tbody").remove();

            let $tbodyTimesheet = jQuery(timesheets).find(".hr_timesheet_portal .o_portal_my_doc_table tbody");
            let $tbodySubtotal = jQuery(timesheets).find(".hr_timesheet_portal .container_subtotal table tbody");
            if ($tbodyTimesheet.length && $tbodyTimesheet.children().length > 0) {
                $tableTimesheet.append($tbodyTimesheet);
            }
            if ($tbodySubtotal.length && $tbodySubtotal.children().length > 0) {
                $tableSubtotal.append($tbodySubtotal);
            }
        });
    },

    _display_failure: function (error) {
        this.$el.prepend(
            jQuery('<div class="alert alert-danger">').text(error.data.message)
        );
    },

    _edit_line(line_id) {
        let $line = this.$(`tr[data-line-id="${line_id}"]`),
            $edit_line = $line.clone();
        this.$("tbody tr.edit").remove();
        this.$("tbody tr").show();
        $line.before($edit_line);
        $edit_line.children("[data-field-name]").each(function () {
            let $this = jQuery(this),
                $input = jQuery("<input>", {
                    class: "form-control",
                    type: $this.data("field-type") || "text",
                    value: $this.data("field-value") || $this.text(),
                    form: "hr_timesheet_portal_form",
                    name: $this.data("field-name"),
                });
            $this.empty().append($input);
        });
        $edit_line.addClass("edit");
        let $form = jQuery("<form>", {
                id: "hr_timesheet_portal_form"
            }),
            $submit = jQuery('<button class="btn btn-primary submit fa fa-cloud-upload">'),
            $cancel = jQuery('<button class="btn btn-outline-primary cancel fa fa-undo" type="reset">');
        $edit_line.children("td:last-child").append($form);
        // $submit.text(_t("Submit"));
        // $cancel.text(_t("Cancel"));
        $form.append($submit, $cancel);
        $edit_line.find("input:first").focus();
        $line.hide();
    },
});

publicWidget.registry.HrTimesheetPortal = HrTimesheetPortal;
