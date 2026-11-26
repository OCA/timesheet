import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";
import {user} from "@web/core/user";

const FORM_ID = "hr_timesheet_portal_form";

export class HrTimesheetPortal extends Interaction {
    static selector = "div.hr_timesheet_portal";

    dynamicContent = {
        // Rows are replaced on every reload, so events are delegated to the root
        _root: {
            "t-on-click": this.onClick,
            "t-on-submit": this.onSubmit,
        },
    };

    onClick(ev) {
        const target = ev.target;
        if (target.closest("h5 .hr_timesheet_portal_add")) {
            this.addLine();
        } else if (
            target.closest("tr[data-line-id].editable i.hr_timesheet_portal_delete")
        ) {
            this.deleteLine(target.closest("tr").dataset.lineId);
        } else if (target.closest("button.submit")) {
            ev.preventDefault();
            this.saveLine(target.closest("tr"));
        } else if (target.closest("button.cancel")) {
            ev.preventDefault();
            this.reloadTimesheets();
        } else {
            const row = target.closest("tr[data-line-id].editable:not(.edit)");
            if (row) {
                this.editLine(row.dataset.lineId);
            }
        }
    }

    onSubmit(ev) {
        ev.preventDefault();
        this.saveLine(this.el.querySelector("tbody tr.edit"));
    }

    async addLine() {
        const [lineId] = await this.rpc(
            this.services.orm.create("account.analytic.line", [
                {
                    user_id: user.userId,
                    account_id: Number(this.el.dataset.accountId) || false,
                    project_id: Number(this.el.dataset.projectId),
                    task_id: Number(this.el.dataset.taskId),
                    unit_amount: 0,
                    name: "/",
                },
            ])
        );
        if (lineId) {
            await this.reloadTimesheets();
            this.editLine(lineId);
        }
    }

    async deleteLine(lineId) {
        if (
            await this.rpc(
                this.services.orm.unlink("account.analytic.line", [Number(lineId)])
            )
        ) {
            await this.reloadTimesheets();
        }
    }

    async saveLine(row) {
        if (!row) {
            return;
        }
        const form = document.getElementById(FORM_ID);
        const data = Object.fromEntries(new FormData(form));
        if (
            await this.rpc(
                this.services.orm.write(
                    "account.analytic.line",
                    [Number(row.dataset.lineId)],
                    data
                )
            )
        ) {
            await this.reloadTimesheets();
        }
    }

    /**
     * Run an ORM call with the UI blocked, showing any error in the block.
     * Returns the call's result, or undefined if it failed.
     */
    async rpc(promise) {
        this.services.ui.block();
        try {
            return await this.waitFor(promise);
        } catch (error) {
            this.displayFailure(error);
        } finally {
            this.services.ui.unblock();
        }
    }

    /**
     * Fetch the page again and swap in its timesheet table body and subtotal.
     */
    async reloadTimesheets() {
        for (const alert of this.el.querySelectorAll(":scope > div.alert")) {
            alert.remove();
        }
        const response = await this.waitFor(fetch(window.location.href));
        const html = await this.waitFor(response.text());
        const fresh = new DOMParser()
            .parseFromString(html, "text/html")
            .querySelector("div.hr_timesheet_portal");
        for (const selector of [
            ".o_portal_my_doc_table",
            ".container_subtotal table",
        ]) {
            const table = this.el.querySelector(selector);
            if (!table) {
                continue;
            }
            for (const tbody of table.querySelectorAll(":scope > tbody")) {
                tbody.remove();
            }
            const tbody = fresh?.querySelector(`${selector} > tbody`);
            if (tbody && tbody.children.length) {
                table.append(document.importNode(tbody, true));
            }
        }
    }

    displayFailure(error) {
        const alert = document.createElement("div");
        alert.className = "alert alert-danger";
        alert.textContent = error.data?.message || error.message || String(error);
        this.el.prepend(alert);
    }

    editLine(lineId) {
        const row = this.el.querySelector(`tr[data-line-id="${lineId}"]`);
        if (!row) {
            return;
        }
        for (const editRow of this.el.querySelectorAll("tbody tr.edit")) {
            editRow.remove();
        }
        for (const other of this.el.querySelectorAll("tbody tr")) {
            other.classList.remove("d-none");
        }
        const editRow = row.cloneNode(true);
        row.before(editRow);
        for (const cell of editRow.querySelectorAll("[data-field-name]")) {
            const input = document.createElement("input");
            input.className = "form-control";
            input.type = cell.dataset.fieldType || "text";
            input.value = cell.dataset.fieldValue || cell.textContent.trim();
            input.name = cell.dataset.fieldName;
            input.setAttribute("form", FORM_ID);
            cell.replaceChildren(input);
        }
        editRow.classList.add("edit");
        const form = document.createElement("form");
        form.id = FORM_ID;
        const submit = document.createElement("button");
        submit.className = "btn btn-primary submit oi";
        submit.dataset.icon = "cloud_upload";
        const cancel = document.createElement("button");
        cancel.className = "btn btn-outline-primary cancel oi";
        cancel.dataset.icon = "undo";
        cancel.type = "reset";
        form.append(submit, cancel);
        editRow.querySelector("td:last-child").append(form);
        editRow.querySelector("input")?.focus();
        row.classList.add("d-none");
    }
}

registry
    .category("public.interactions")
    .add("hr_timesheet_portal.hr_timesheet_portal", HrTimesheetPortal);
