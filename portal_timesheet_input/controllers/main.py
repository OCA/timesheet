# Copyright 2025 Acysos S.L. (https://www.acysos.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, datetime, timedelta

from odoo import _, http
from odoo.http import request

from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal


class PortalTimesheetInput(TimesheetCustomerPortal):
    """Portal Timesheet Input Controller."""

    @http.route(["/my/timesheet/input"], type="http", auth="user", website=True)
    def timesheet_input_grid(self, week_start=None, **kwargs):
        """Render the timesheet input grid page."""
        # 1. Determine Week Range
        today = date.today()
        if week_start:
            try:
                start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
            except ValueError:
                start_date = today - timedelta(days=today.weekday())
        else:
            # Monday of current week
            start_date = today - timedelta(days=today.weekday())

        end_date = start_date + timedelta(days=6)

        # 2. Prepare Days Header
        days = []
        current = start_date
        while current <= end_date:
            days.append(
                {
                    "date": current,
                    "name": current.strftime("%a %d"),
                    "day_str": current.strftime("%Y-%m-%d"),
                }
            )
            current += timedelta(days=1)

        # 3. Fetch Data
        partner = request.env.user.partner_id
        employee = (
            request.env["hr.employee.public"]
            .sudo()
            .search([("user_id", "=", request.env.user.id)], limit=1)
        )
        if not employee:
            return request.render(
                "portal_timesheet_input.timesheet_error",
                {
                    "page_name": "timesheet_input",
                    "error_message": _(
                        "You must be linked to an employee to enter timesheets."
                    ),
                },
            )

        domain = [
            ("employee_id", "=", employee.id),
            ("date", ">=", start_date),
            ("date", "<=", end_date),
            # Ensure project is set
            ("project_id", "!=", False),
        ]
        timesheets = request.env["account.analytic.line"].sudo().search(domain)
        grid_data = {}

        # Key can be 'task_ID' or 'proj_ID_no_task'
        def get_key(line):
            if line.task_id:
                return f"task_{line.task_id.id}"
            return f"proj_{line.project_id.id}"

        # Pre-fill with existing entries
        for line in timesheets:
            key = get_key(line)
            if key not in grid_data:
                grid_data[key] = {
                    "type": "task" if line.task_id else "project",
                    "id": (line.task_id.id if line.task_id else line.project_id.id),
                    "name": (
                        line.task_id.name if line.task_id else line.project_id.name
                    ),
                    "project_name": line.project_id.name,
                    "project_id": line.project_id.id,
                    "days": {},
                }

            day_str = line.date.strftime("%Y-%m-%d")
            grid_data[key]["days"][day_str] = (
                grid_data[key]["days"].get(day_str, 0.0) + line.unit_amount
            )

        # Convert grid_data to sorted list
        rows = sorted(grid_data.values(), key=lambda x: (x["project_name"], x["name"]))

        # Pass available projects/tasks for the "Add Line" feature
        # Standard portal domain for projects
        projects = (
            request.env["project.project"]
            .sudo()
            .search(
                [
                    ("privacy_visibility", "=", "portal"),
                    (
                        "message_partner_ids",
                        "child_of",
                        [partner.commercial_partner_id.id],
                    ),
                ]
            )
        )

        values = {
            "page_name": "timesheet_input_grid",
            "week_start": start_date.strftime("%Y-%m-%d"),
            "prev_week": (start_date - timedelta(days=7)).strftime("%Y-%m-%d"),
            "next_week": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            "days": days,
            "rows": rows,
            "projects": projects,
        }
        return request.render("portal_timesheet_input.timesheet_input_grid", values)

    @http.route(["/my/timesheet/save_grid"], type="json", auth="user", website=True)
    def save_grid_inputs(self, inputs, week_start):
        """
        inputs: list of {
            'project_id': int, 'task_id': int (opt),
            'date': str, 'unit_amount': float
        }
        """
        employee = (
            request.env["hr.employee.public"]
            .sudo()
            .search([("user_id", "=", request.env.user.id)], limit=1)
        )
        if not employee:
            return {"error": "User not linked to employee"}

        # We will process cell by cell.
        timesheet_sudo = request.env["account.analytic.line"].sudo()

        for entry in inputs:
            try:
                date_input = entry.get("date")
                date_obj = datetime.strptime(date_input, "%Y-%m-%d").date()
                amount = float(entry.get("unit_amount") or 0.0)
                project_id = int(entry.get("project_id"))
                task_id = int(entry.get("task_id")) if entry.get("task_id") else False

                domain = [
                    ("employee_id", "=", employee.id),
                    ("date", "=", date_obj),
                    ("project_id", "=", project_id),
                    ("task_id", "=", task_id),
                ]

                existing = timesheet_sudo.search(domain)

                if amount == 0.0:
                    if existing:
                        existing.unlink()
                else:
                    if existing:
                        current_total = sum(existing.mapped("unit_amount"))
                        if current_total != amount:
                            diff = amount - current_total
                            existing[-1].write(
                                {"unit_amount": existing[-1].unit_amount + diff}
                            )

                    else:
                        vals = {
                            "project_id": project_id,
                            "task_id": task_id,
                            "date": date_obj,
                            "unit_amount": amount,
                            "employee_id": employee.id,
                            "name": "/",  # Default description
                        }
                        timesheet_sudo.create(vals)
            except (ValueError, IndexError, TypeError) as e:
                return {"error": str(e)}

        return {"success": True}

    @http.route(["/my/timesheet/get_tasks"], type="json", auth="user", website=True)
    def get_project_tasks(self, project_id):
        """Retrieve tasks for a specific project."""
        domain = [
            ("project_id", "=", int(project_id)),
            # Add visibility checks similar to search
            ("project_id.privacy_visibility", "=", "portal"),
        ]
        tasks = request.env["project.task"].sudo().search(domain)
        return [{"id": t.id, "name": t.name} for t in tasks]
