odoo.define('hr_timesheet_task.sheet', function (require) {
    'use strict';

    var core = require('web.core');
    var data = require('web.data');
    var form_common = require('web.form_common');
    var Model = require('web.DataModel');
    var time = require('web.time');
    var hr_timesheet_sheet = require('hr_timesheet_sheet.sheet');

    var WeeklyTimesheet = core.form_custom_registry.get('weekly_timesheet').extend({
        events: {
            'click .oe_timesheet_weekly_account a': 'go_to',
            'click .oe_timesheet_weekly_account_task a': 'go_to_task',
        },
        go_to_task: function(event) {
            var id = JSON.parse($(event.target).data('id'));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'project.task',
                res_id: id,
                views: [[false, 'form']],
                target: 'current',
            });
        },
        go_to: function(event) {
            var id = JSON.parse($(event.target).data('id'));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'account.analytic.account',
                res_id: id,
                views: [[false, 'form']],
            });
        },
        initialize_content: function() {
            if(this.setting) {
                return;
            }

            // don't render anything until we have date_to and date_from
            if (!this.get('date_to') || !this.get('date_from')) {
                return;
            }

            // it's important to use those vars to avoid race conditions
            var dates;
            var accounts;
            var accounts_by_tasks;
            var timesheet_lines;
            var task_names;
            var account_names;
            var default_get;
            var self = this;
            return self.render_drop.add(new Model('account.analytic.line').call('default_get', [
                ['account_id','general_account_id','journal_id','date','name','user_id','product_id','product_uom_id','amount','unit_amount','is_timesheet','task_id'],
                new data.CompoundContext({'user_id': self.get('user_id'), 'default_is_timesheet': true})
            ]).then(function(result) {
                default_get = result;
                // calculating dates
                dates = [];
                var start = self.get('date_from');
                var end = self.get('date_to');
                while (start <= end) {
                    dates.push(start);
                    var m_start = moment(start).add(1, 'days');
                    start = m_start.toDate();
                }

                timesheet_lines = _(self.get('sheets')).chain()
                    .map(function(el) {
                        // much simpler to use only the id in all cases
                        if (typeof(el.account_id) === 'object')
                            el.account_id = el.account_id[0];
                        if (typeof(el.task_id) === 'object')
                            el.task_id = el.task_id[0];
                        return el;
                    }).value();

                // group by account
                accounts = _.groupBy(timesheet_lines, function(el) {
                    return el.account_id;
                });

                // group by account and task
                accounts_by_tasks = _.groupBy(timesheet_lines, function(el) {
                    return [el.account_id, el.task_id];
                });

                accounts = _(accounts_by_tasks).chain().map(function(lines, account_id_task_id) {
                    var account_id = lines[0].account_id;
                    var account_defaults = _.extend({}, default_get, (accounts[account_id] || {}).value || {});
                    // group by days
                    account_id = (account_id === 'false')? false : Number(account_id);
                    var index = _.groupBy(lines, 'date');
                    var days = _.map(dates, function(date) {
                        var day = {day: date, lines: index[time.date_to_str(date)] || []};
                        // add line where we will insert/remove hours
                        var to_add = _.find(day.lines, function(line) { return line.name === self.description_line; });
                        if (to_add) {
                            day.lines = _.without(day.lines, to_add);
                            day.lines.unshift(to_add);
                        } else {
                            day.lines.unshift(_.extend(_.clone(account_defaults), {
                                name: self.description_line,
                                unit_amount: 0,
                                date: time.date_to_str(date),
                                account_id: account_id,
                                task_id: lines[0].task_id,
                            }));
                        }
                        return day;
                    });
                    return {account_task: account_id_task_id, account: account_id, days: days, account_defaults: account_defaults, task: lines[0].task_id};
                }).value();

                // we need the name_get of the analytic accounts
                return new Model('account.analytic.account').call('name_get', [_.pluck(accounts, 'account'),
                    new data.CompoundContext()]).then(function(result) {
                    account_names = {};
                    _.each(result, function(el) {
                        account_names[el[0]] = el[1];
                    });
                    // we need the name_get of the tasks
                    return new Model('project.task').call('name_get', [_(accounts).chain().pluck('task').filter(function(el) { return el; }).value(),
                        new data.CompoundContext()]).then(function(result) {
                        task_names = {};
                        _.each(result, function(el) {
                            task_names[el[0]] = el[1];
                        });
                        accounts = _.sortBy(accounts, function(el) {
                            return account_names[el.account];
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
            if (self.dfm) {
                self.dfm.destroy();
            }

            self.$('.oe_timesheet_weekly_add_row').show();
            self.dfm = new form_common.DefaultFieldManager(self);
            self.dfm.extend_field_desc({
                account: {
                    relation: 'account.analytic.account',
                },
                task: {
                    relation: 'project.task',
                },
            });
            var FieldMany2One = core.form_widget_registry.get('many2one');
            self.account_m2o = new FieldMany2One(self.dfm, {
                attrs: {
                    options: '{"create": False, "create_edit": False, "no_create": True}',
                    name: 'account',
                    type: 'many2one',
                    modifiers: '{"required": true}',
                },
            });

            self.task_m2o = new FieldMany2One(self.dfm, {
                attrs: {
                    options: '{"create": False, "create_edit": False, "no_create": True}',
                    name: 'task',
                    type: 'many2one',
                    domain: [
                        // at this moment, it is always an empty list
                        ['project_id.analytic_account_id','=',self.account_m2o.get_value()]
                    ],
                },
            });
            self.task_m2o.prependTo(this.$('.o_add_timesheet_line > div'));

            self.account_m2o.prependTo(this.$('.o_add_timesheet_line > div')).then(function() {
                self.account_m2o.$el.addClass('oe_edit_only');
            });

            self.account_m2o.$input.focusout(function(){
                self.onchange_account_id();
            });

            self.$('.oe_timesheet_button_add').click(function() {
                var id = self.account_m2o.get_value();
                var task_id = self.task_m2o.get_value();
                if (id === false) {
                    self.dfm.set({display_invalid_fields: true});
                    return;
                }

                var ops = self.generate_o2m_value();
                ops.push(_.extend({}, self.default_get, {
                    name: self.description_line,
                    unit_amount: 0,
                    date: time.date_to_str(self.dates[0]),
                    account_id: id,
                    task_id: task_id,
                }));

                self.set({sheets: ops});
                self.destroy_content();
            });
        },

        onchange_account_id: function() {
            var self = this;
            var account_id = self.account_m2o.get_value();
            if (account_id === false) { return; }

            self.task_m2o.node.attrs.domain = [
                // show only tasks linked to the selected project
                ['project_id.analytic_account_id','=',account_id],
                // ignore tasks already in the timesheet
                ['id', 'not in', _.pluck(self.accounts, 'task')],
            ];
            self.task_m2o.node.attrs.context = {'account_id': account_id};
            self.task_m2o.set_value(false);
            self.task_m2o.render_value();
        },

        get_box: function(account, day_count) {
            return this.$('[data-account-task="' + account.account_task + '"][data-day-count="' + day_count + '"]');
        },
    });

    core.form_custom_registry.add('weekly_timesheet', WeeklyTimesheet);
});
