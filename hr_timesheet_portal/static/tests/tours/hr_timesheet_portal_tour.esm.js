import {registry} from "@web/core/registry";

const LINE = "Portal tour line";
const ROOT = "div.hr_timesheet_portal";

// The add and delete icons only show on hover (CSS :hover), which a tour
// can't trigger, so these steps wait for their container and click the icon.
registry.category("web_tour.tours").add("hr_timesheet_portal_tour", {
    steps: () => [
        {
            content: "Add a timesheet line",
            trigger: `${ROOT} h5:has(.hr_timesheet_portal_add)`,
            run(helpers) {
                helpers.anchor.querySelector(".hr_timesheet_portal_add").click();
            },
        },
        {
            content: "Fill in the description",
            trigger: `${ROOT} tr.edit input[name=name]`,
            run: `edit ${LINE}`,
        },
        {
            content: "Fill in the hours",
            trigger: `${ROOT} tr.edit input[name=unit_amount]`,
            run: "edit 1.5",
        },
        {
            content: "Save the line",
            trigger: `${ROOT} tr.edit button.submit`,
            run: "click",
        },
        {
            content: "Delete the saved line",
            trigger: `${ROOT} tbody tr.editable:not(.edit):contains(${LINE})`,
            run(helpers) {
                helpers.anchor.querySelector(".hr_timesheet_portal_delete").click();
            },
        },
        {
            content: "The line is gone",
            trigger: `${ROOT}:not(:has(tbody tr:contains(${LINE})))`,
        },
    ],
});
