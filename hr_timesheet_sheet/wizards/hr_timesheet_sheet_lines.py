# Copyright 2018-2020 ForgeFlow, S.L.
# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

empty_name = "/"


class AbstractSheetLine(models.AbstractModel):
    _name = "hr_timesheet.sheet.line.abstract"
    _description = "Abstract Timesheet Sheet Line"

    sheet_id = fields.Many2one(comodel_name="hr_timesheet.sheet", ondelete="cascade")
    date = fields.Date()
    project_id = fields.Many2one(comodel_name="project.project", string="Project")
    task_id = fields.Many2one(comodel_name="project.task", string="Task")
    unit_amount = fields.Float(string="Quantity", default=0.0)
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")

    def get_unique_id(self):
        """Hook for extensions"""
        self.ensure_one()
        return {"project_id": self.project_id, "task_id": self.task_id}


class SheetLine(models.TransientModel):
    _name = "hr_timesheet.sheet.line"
    _inherit = "hr_timesheet.sheet.line.abstract"
    _description = "Timesheet Sheet Line"

    value_x = fields.Char(string="Date Name")
    value_y = fields.Char(string="Project Name")
    new_line_id = fields.Integer(default=0)

    @api.onchange("unit_amount")
    def onchange_unit_amount(self):
        """This method is called when filling a cell of the matrix."""
        self.ensure_one()
        sheet = self._get_sheet()
        if not sheet:
            return {
                "warning": {
                    "title": self.env._("Warning"),
                    "message": self.env._("Save the Timesheet Sheet first."),
                }
            }
        sheet.add_new_line(self)

    @api.model
    def _get_sheet(self):
        sheet = (self._origin or self).sheet_id
        if not sheet:
            model = self.env.context.get("params", {}).get("model", "")
            obj_id = self.env.context.get("params", {}).get("id")
            if model == "hr_timesheet.sheet" and isinstance(obj_id, int):
                sheet = self.env["hr_timesheet.sheet"].browse(obj_id)
        return sheet


class SheetNewAnalyticLine(models.TransientModel):
    _name = "hr_timesheet.sheet.new.analytic.line"
    _inherit = "hr_timesheet.sheet.line.abstract"
    _description = "Timesheet Sheet New Analytic Line"

    @api.model
    def _is_similar_analytic_line(self, aal):
        """Hook for extensions"""
        return (
            aal.date == self.date
            and aal.project_id.id == self.project_id.id
            and aal.task_id.id == self.task_id.id
        )

    @api.model
    def _update_analytic_lines(self):
        sheet = self.sheet_id
        timesheets = sheet.timesheet_ids.filtered(
            lambda aal: self._is_similar_analytic_line(aal)
        )
        new_ts = timesheets.filtered(lambda t: t.name == empty_name)
        amount = sum(t.unit_amount for t in timesheets)
        diff_amount = self.unit_amount - amount
        if len(new_ts) > 1:
            new_ts = new_ts.merge_timesheets()
            sheet._sheet_write("timesheet_ids", sheet.timesheet_ids.exists())
        if not diff_amount:
            return
        if new_ts:
            unit_amount = new_ts.unit_amount + diff_amount
            if unit_amount:
                new_ts.write({"unit_amount": unit_amount})
            else:
                new_ts.unlink()
                sheet._sheet_write("timesheet_ids", sheet.timesheet_ids.exists())
        else:
            new_ts_values = sheet._prepare_new_line(self)
            new_ts_values.update({"name": empty_name, "unit_amount": diff_amount})
            self.env["account.analytic.line"]._sheet_create(new_ts_values)
