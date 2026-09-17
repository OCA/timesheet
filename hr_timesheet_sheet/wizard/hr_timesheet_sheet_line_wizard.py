from odoo import api, fields, models


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
