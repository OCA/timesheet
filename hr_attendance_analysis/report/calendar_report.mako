## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <% setLang(objects[0].company_id.partner_id.lang) %>
    <% from datetime import datetime %>
    %for employee in objects :
    <h2>${_("Employee: ")} ${ employee.name or ''|entity }</h2>
    <table style="width:100%" border="1">
        <thead style="border-bottom: solid; background-color: WhiteSmoke">
            <tr style="page-break-inside: avoid">
                <th style="text-align:left">${_("Date")}</th>
                <th style="text-align:left">${_("Day of week")}</th>
                %if max_per_day() >= 1:
                    <th style="text-align:left">${_("First Sign In")}</th>
                    <th style="text-align:left">${_("First Sign Out")}</th>
                %endif
                %if max_per_day() >= 2:
                    <th style="text-align:left">${_("Second Sign In")}</th>
                    <th style="text-align:left">${_("Second Sign Out")}</th>
                %endif
                %if max_per_day() >= 3:
                    <th style="text-align:left">${_("Third Sign In")}</th>
                    <th style="text-align:left">${_("Third Sign Out")}</th>
                %endif
                %if max_per_day() >= 4:
                    <th style="text-align:left">${_("Fourth Sign In")}</th>
                    <th style="text-align:left">${_("Fourth Sign Out")}</th>
                %endif
                <th style="text-align:right">${_("Due")}</th>
                <th style="text-align:right">${_("Working Hours")}</th>
                <th style="text-align:right">${_("Overtime")}</th>
                <th style="text-align:right">${_("Negative")}</th>
                <th style="text-align:right">${_("Leave")}</th>
            </tr>
        </thead>
        <% first_done = 0 %>
        %for day in sorted(days_by_employee(employee.id).iterkeys()) :
            %if datetime.strptime(day, '%Y-%m-%d').day == 1 or not first_done:
                <tr style="page-break-inside: avoid" >
                    <td colspan="15">
                    <strong>${ month_name(day) | entity }</strong>
                    </td>
                </tr>
            <% first_done = 1 %>
            %endif
            <tr style="page-break-inside: avoid">
                <td style="text-align:left">${ formatLang(day, date=True) | entity }</td>
                <td style="text-align:left">${ day_of_week(day) | entity }</td>
                %if max_per_day() >= 1:
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signin_1'] | entity }</td>
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signout_1'] | entity }</td>
                %endif
                %if max_per_day() >= 2:
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signin_2'] | entity }</td>
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signout_2'] | entity }</td>
                %endif
                %if max_per_day() >= 3:
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signin_3'] | entity }</td>
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signout_3'] | entity }</td>
                %endif
                %if max_per_day() >= 4:
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signin_4'] | entity }</td>
                    <td style="text-align:left">${ days_by_employee(employee.id)[day]['signout_4'] | entity }</td>
                %endif
                <td style="text-align:right">${ (days_by_employee(employee.id)[day]['due']) | entity }</td>
                <td style="text-align:right">${ (days_by_employee(employee.id)[day]['attendances']) | entity }</td>
                %if days_by_employee(employee.id)[day]['overtime'] != '00:00':
                    <td style="text-align:right; background-color:LightGreen">${ (days_by_employee(employee.id)[day]['overtime']) | entity }</td>
                %else:
                    <td style="text-align:right">${ (days_by_employee(employee.id)[day]['overtime']) | entity }</td>
                %endif
                %if days_by_employee(employee.id)[day]['negative'] != '00:00':
                    <td style="text-align:right; background-color: Tomato">${ (days_by_employee(employee.id)[day]['negative']) | entity }</td>
                %else:
                    <td style="text-align:right">${ (days_by_employee(employee.id)[day]['negative']) | entity }</td>
                %endif
                %if days_by_employee(employee.id)[day]['leaves'] != '00:00':
                    <td style="text-align:right; background-color: Silver">${ (days_by_employee(employee.id)[day]['leaves']) | entity }</td>
                %else:
                    <td style="text-align:right">${ (days_by_employee(employee.id)[day]['leaves']) | entity }</td>
                %endif
            </tr>
        %endfor
        <tfoot style="font-weight:bold">
        <tr style="page-break-inside: avoid">
            <td style="text-align:left">${_("Totals")} </td>
            <td></td>
            %if max_per_day() >= 1:
                <td></td>
                <td></td>
            %endif
            %if max_per_day() >= 2:
                <td></td>
                <td></td>
            %endif
            %if max_per_day() >= 3:
                <td></td>
                <td></td>
            %endif
            %if max_per_day() >= 4:
                <td></td>
                <td></td>
            %endif
            <td style="border-top:1px solid #000; text-align:right">${ (totals_by_employee(employee.id)['total_due']) | entity }</td>
            <td style="border-top:1px solid #000; text-align:right">${ (totals_by_employee(employee.id)['total_attendances']) | entity }</td>
            <td style="border-top:1px solid #000; text-align:right">${ (totals_by_employee(employee.id)['total_overtime']) | entity }</td>
            <td style="border-top:1px solid #000; text-align:right">${ (totals_by_employee(employee.id)['total_negative']) | entity }</td>
            <td style="border-top:1px solid #000; text-align:right">${ (totals_by_employee(employee.id)['total_leaves']) | entity }</td>
        </tr>
        </tfoot>
    </table>
    <br/>
    <table>
        <thead>
            <tr>
                <th style="text-align:left">${_("Overtime type")}</th>
                <th style="text-align:right">${_("Total")}</th>
            </tr>
        </thead>
        %for type in totals_by_employee(employee.id)['total_types']:
            <tr>
                <td style="text-align:left">
                    ${type | entity}
                </td>
                <td style="text-align:right">
                    ${(totals_by_employee(employee.id)['total_types'][type]) | entity}
                </td>
            </tr>
        %endfor
    </table>
    <p style="page-break-after:always; height: 1px"></p>
    %endfor
</body>
</html>
