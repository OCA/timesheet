/* global window */
/* Copyright 2025 Acysos S.L. (https://www.acysos.com)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.TimesheetInputGrid = publicWidget.Widget.extend({
    selector: ".o_portal_timesheet_input_grid",
    events: {
        "change .timesheet-input": "_onInputChange",
        "click #btn_save_timesheet": "_onSave",
        "change #new_line_project_id": "_onProjectChange",
        "click #btn_add_line": "_onAddLine",
    },

    start: function () {
        this._super.apply(this, arguments);
        this._computeTotals();
    },

    _onInputChange: function () {
        this._computeTotals();
    },

    _computeTotals: function () {
        var grandTotal = 0.0;
        var colTotals = {};

        // Reset col totals
        this.$("tfoot .col-total").each(function () {
            colTotals[$(this).attr("data-date")] = 0.0;
        });

        // Loop rows
        this.$("tbody tr")
            .not(".add-line-row")
            .each(function () {
                var $row = $(this);
                var rowTotal = 0.0;

                $row.find(".timesheet-input").each(function () {
                    var val = parseFloat($(this).val()) || 0.0;
                    var date = $(this).attr("data-date");

                    rowTotal += val;
                    if (colTotals[date] !== undefined) {
                        colTotals[date] += val;
                    }
                });

                $row.find(".row-total").text(rowTotal.toFixed(2));
                grandTotal += rowTotal;
            });

        // Update footer
        this.$("tfoot .col-total").each(function () {
            var date = $(this).attr("data-date");
            $(this).text((colTotals[date] || 0.0).toFixed(2));
        });
        this.$(".grand-total").text(grandTotal.toFixed(2));
    },

    _onSave: async function () {
        var inputs = [];
        var week_start = this.$("#week_start_date").val();

        // Collect data
        this.$("tbody tr")
            .not(".add-line-row")
            .each(function () {
                var $row = $(this);
                var projectId = $row.attr("data-project-id");
                var taskId = $row.attr("data-task-id");

                $row.find(".timesheet-input").each(function () {
                    // Keep as string to detect empty vs 0? No, treating 0 as delete.
                    var val = $(this).val();
                    var date = $(this).attr("data-date");
                    // We send everything, let backend handle 0s
                    inputs.push({
                        project_id: projectId,
                        task_id: taskId,
                        date: date,
                        unit_amount: val,
                    });
                });
            });

        try {
            const result = await rpc("/my/timesheet/save_grid", {
                inputs: inputs,
                week_start: week_start,
            });
            if (result && result.success) {
                window.location.reload();
            } else {
                this.env.services.notification.add(
                    "Error saving: " +
                        (result && result.error ? result.error : "Unknown error"),
                    {type: "danger"}
                );
            }
        } catch (err) {
            this.env.services.notification.add(
                "Error saving: " + (err && err.message ? err.message : err),
                {type: "danger"}
            );
        }
    },

    _onProjectChange: function (ev) {
        var projectId = $(ev.currentTarget).val();
        var $taskSelect = this.$("#new_line_task_id");
        $taskSelect.empty().append('<option value="">Select Task...</option>');

        if (projectId) {
            rpc("/my/timesheet/get_tasks", {project_id: projectId}).then(
                function (tasks) {
                    $.each(tasks, function (i, task) {
                        $taskSelect.append(
                            $("<option>", {
                                value: task.id,
                                text: task.name,
                            })
                        );
                    });
                    $taskSelect.removeAttr("disabled");
                }
            );
        } else {
            $taskSelect.attr("disabled", "disabled");
        }
    },

    _onAddLine: function () {
        var projectId = this.$("#new_line_project_id").val();
        var projectName = this.$("#new_line_project_id option:selected").text();
        var taskId = this.$("#new_line_task_id").val();
        var taskName = this.$("#new_line_task_id option:selected").text();

        if (!projectId) {
            this.env.services.notification.add("Please select a project.", {
                type: "warning",
            });
            return;
        }

        // Create new row
        var $newRow = $("<tr>")
            .attr("data-project-id", projectId)
            .attr("data-task-id", taskId || "")
            .attr("data-type", taskId ? "task" : "project");

        var $nameTd = $("<td>").addClass("align-middle");
        $nameTd.append($("<div>").addClass("font-weight-bold").text(projectName));
        if (taskId) {
            $nameTd.append($("<div>").addClass("small text-muted").text(taskName));
        }
        $newRow.append($nameTd);

        this.$("tfoot .col-total").each(function () {
            var date = $(this).attr("data-date");

            var $td = $("<td>").addClass("p-0");
            var $input = $("<input>", {
                type: "number",
                step: "0.5",
                class: "form-control border-0 text-center timesheet-input",
                "data-date": date,
            });
            $td.append($input);
            $newRow.append($td);
        });

        // Total column
        $newRow.append(
            $("<td>")
                .addClass("text-center align-middle row-total font-weight-bold")
                .text("0.00")
        );

        // Insert before the last row (Add Line row)
        $(".add-line-row").before($newRow);

        // Clear inputs
        this.$("#new_line_task_id").val("").trigger("change");
    },
});
