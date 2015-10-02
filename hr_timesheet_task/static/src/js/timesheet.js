openerp.hr_timesheet_task = function(instance) { 

    var module = instance.hr_timesheet_sheet

    module.WeeklyTimesheet = module.WeeklyTimesheet.extend({
        events: {
            "click .oe_timesheet_weekly_account a": "go_to",
            "click .oe_timesheet_weekly_task a": "go_to_task",
        },
        go_to_task : function(event) {
            var id = JSON.parse($(event.target).data("task-id"));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: "project.task",
                res_id: id,
                views: [[false, 'form']],
                target: 'current'
            });
        },
        initialize_content: function() {
            var self = this;
            if (self.setting)
                return;
            // don't render anything until we have date_to and date_from
            if (!self.get("date_to") || !self.get("date_from"))
                return;
            this.destroy_content();

            // it's important to use those vars to avoid race conditions
            var dates;
            var accounts;
            var account_names;
            var task_names;
            var default_get;
            return this.render_drop.add(new instance.web.Model("hr.analytic.timesheet").call("default_get", [
                ['account_id','task_id','general_account_id','journal_id','date','name','user_id','product_id','product_uom_id','to_invoice','amount','unit_amount'],
                new instance.web.CompoundContext({'user_id': self.get('user_id')})]).then(function(result) {
                default_get = result;
                // calculating dates
                dates = [];
                var start = self.get("date_from");
                var end = self.get("date_to");
                while (start <= end) {
                    dates.push(start);
                    start = start.clone().addDays(1);
                }

                timesheet_lines = _(self.get("sheets")).chain()
                .map(function(el) {
                    // much simpler to use only the id in all cases
                    if (typeof(el.account_id) === "object")
                        el.account_id = el.account_id[0];
                    if (typeof(el.task_id) === "object")
                        el.task_id = el.task_id[0];
                    return el;
                }).value();

                // group by account
                var timesheet_lines_by_account_id = _.groupBy(timesheet_lines, function(el) {
                    return el.account_id;
                });

                // group by account and task
                var timesheet_lines_by_account_id_task_id = _.groupBy(timesheet_lines, function(el) {
                    return [el.account_id, el.task_id];
                });

                var account_ids = _.map(_.keys(timesheet_lines_by_account_id), function(el) { return el === "false" ? false : Number(el) });

                return new instance.web.Model("hr.analytic.timesheet").call("multi_on_change_account_id", [[], account_ids,
                    new instance.web.CompoundContext({'user_id': self.get('user_id')})]).then(function(accounts_defaults) {
                    accounts = _(timesheet_lines_by_account_id_task_id).chain().map(function(lines, account_id_task_id) {
                        account_defaults = _.extend({}, default_get, (accounts_defaults[lines[0].account_id] || {}).value || {});
                        // group by days
                        var index = _.groupBy(lines, "date");
                        var days = _.map(dates, function(date) {
                            var day = {day: date, lines: index[instance.web.date_to_str(date)] || []};
                            // add line where we will insert/remove hours
                            var to_add = _.find(day.lines, function(line) { return line.name === self.description_line });
                            if (to_add) {
                                day.lines = _.without(day.lines, to_add);
                                day.lines.unshift(to_add);
                            } else {
                                day.lines.unshift(_.extend(_.clone(account_defaults), {
                                    name: self.description_line,
                                    unit_amount: 0,
                                    date: instance.web.date_to_str(date),
                                    account_id: lines[0].account_id,
                                    task_id: lines[0].task_id,
                                }));
                            }
                            return day;
                        });
                        return {account_task: account_id_task_id, account: lines[0].account_id, task: lines[0].task_id, days: days, account_defaults: account_defaults};
                    }).value();

                    // we need the name_get of the analytic accounts
                    return new instance.web.Model("account.analytic.account").call("name_get", [_.pluck(accounts, "account"),
                        new instance.web.CompoundContext()]).then(function(result) {
                        account_names = {};
                        _.each(result, function(el) {
                            account_names[el[0]] = el[1];
                        });
                        // we need the name_get of the tasks
                        return new instance.web.Model("project.task").call("name_get", [_(accounts).chain().pluck("task").filter(function(el) { return el; }).value(),
                            new instance.web.CompoundContext()]).then(function(result) {
                            task_names = {};
                            _.each(result, function(el) {
                                task_names[el[0]] = el[1];
                            });
                            accounts = _.sortBy(accounts, function(el) {
                                return account_names[el.account];
                            });
                        });
                    });
                });
            })).then(function(result) {
                // we put all the gathered data in self, then we render
                self.dates = dates;
                self.accounts = accounts;
                self.account_names = account_names;
                self.task_names = task_names;
                self.default_get = default_get;
                //real rendering
                self.display_data();
            });
        },
        init_add_account: function() {
            var self = this;
            if (self.dfm)
                return;
            self.$(".oe_timesheet_weekly_add_row").show();
            self.dfm = new instance.web.form.DefaultFieldManager(self);
            self.dfm.extend_field_desc({
                account: {
                    relation: "account.analytic.account",
                },
                task: {
                    relation: "project.task",
                },
            });
            self.account_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                attrs: {
                    name: "account",
                    type: "many2one",
                    domain: [
                        ['type','in',['normal', 'contract']],
                        ['state', '!=', 'close'],
                        ['use_timesheets','=',1],
                    ],
                    context: {
                        default_use_timesheets: 1,
                        default_type: "contract",
                    },
                    modifiers: '{"required": true}',
                },
            });
            self.task_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                attrs: {
                    name: "task",
                    type: "many2one",
                    domain: [
                        // at this moment, it is always an empty list 
                        ['project_id.analytic_account_id','=',self.account_m2o.get_value()]
                    ],
                },
            });
            self.task_m2o.prependTo(self.$(".oe_timesheet_weekly_add_row td"));
            self.account_m2o.prependTo(self.$(".oe_timesheet_weekly_add_row td"));

            // when account_m2o loses focus, value can be changed, 
            // update task_m2o to show only tasks related to the selected project
            self.account_m2o.$input.focusout(function(){
                self.onchange_account_id()
            });

            self.$(".oe_timesheet_weekly_add_row button").click(function() {
                var id = self.account_m2o.get_value();
                if (id === false) {
                    self.dfm.set({display_invalid_fields: true});
                    return;
                }
                var ops = self.generate_o2m_value();
                new instance.web.Model("hr.analytic.timesheet").call("on_change_account_id", [[], id]).then(function(res) {
                    var def = _.extend({}, self.default_get, res.value, {
                        name: self.description_line,
                        unit_amount: 0,
                        date: instance.web.date_to_str(self.dates[0]),
                        account_id: id,
                        task_id: self.task_m2o.get_value(),
                    });
                    ops.push(def);
                    self.set({"sheets": ops});
                });
            });
        },
        onchange_account_id: function() {
            var self = this
            var account_id = self.account_m2o.get_value();
            if (account_id === false) { return; }
            self.task_m2o.node.attrs.domain = [
               // show only tasks linked to the selected project
               ['project_id.analytic_account_id','=',account_id],
               // ignore tasks already in the timesheet
               ['id', 'not in', _.pluck(self.accounts, "task")],
            ]
            self.task_m2o.node.attrs.context = {'account_id': account_id};
            self.task_m2o.set_value(false);
            self.task_m2o.render_value();
        },
        get_box: function(account, day_count) {
            return this.$('[data-account-task="' + account.account_task + '"][data-day-count="' + day_count + '"]');
        },
        get_total: function(account) {
            return this.$('[data-account-task-total="' + account.account_task + '"]');
        },
    });
};
