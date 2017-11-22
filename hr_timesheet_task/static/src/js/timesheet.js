openerp.hr_timesheet_task = function(instance) {

    var module = instance.hr_timesheet_sheet,
        date_to_str = instance.web.date_to_str;

    module.WeeklyTimesheet.include({
        events: {
            "click .oe_timesheet_weekly_account a": "go_to",
            "click .oe_timesheet_weekly_task a": "go_to_task",
        },
        task_names: {},
        go_to_task : function(event) {
            var id = JSON.parse($(event.target).data("task-id"));
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: "project.task",
                res_id: id,
                views: [[false, 'form']],
                target: 'current'
            });
        },
        initialize_content: function() {
            var deferred = this._super.apply(this, arguments);
            if(!deferred)
            {
                // this happens when super exits early
                return;
            }
            return deferred.then(
            ).then(
                this.proxy('initialize_content_group')
            ).then(
                this.proxy('initialize_content_tasks')
            ).then(
                this.proxy('display_data')
            );
        },
        initialize_content_tasks: function() {
            var self = this;
            this.tasks = _.chain(this.get('sheets'))
            .groupBy('task_id')
            .map(function(x) {return self._m2o_id(x[0].task_id);})
            .value();

            return new instance.web.Model('project.task')
            .call(
                "name_get",
                [
                    _.filter(this.tasks, _.identity),
                    new instance.web.CompoundContext()
                ]
            ).then(function(names)
            {
                self.task_names = {
                    false: instance.web._t('No task'),
                };
                _.extend(self.task_names, _.object(names));
            });
        },
        initialize_content_group: function() {
            var
            self = this,
            existing_groups = _.chain(this.get('sheets'))
                .groupBy(self.proxy('initialize_content_group_by'))
                .keys();

            this.accounts = _.chain(this.accounts)
            .map(function(account)
            {
                return _.chain(account.days)
                .map(function(day) { return day.lines; })
                .flatten(true)
                .groupBy(self.proxy('initialize_content_group_by'))
                .filter(function(records, group) {
                    return !existing_groups.intersection([group]).isEmpty()
                        .value();
                })
                .map(_.bind(
                    self.initialize_content_group_clone_account,
                    self, account
                ))
                .value();
            })
            .flatten(true)
            .sortBy(function(account) {
                return _.str.sprintf(
                    '%s - %s',
                    self.task_names[account.task_id],
                    self.account_names[account.account]
                );
            })
            .value();

        },
        initialize_content_group_clone_account: function(account, records) {
            var self = this,
                clone = _.clone(account);
            clone.task_id = self._m2o_id(records[0].task_id);
            clone.account_defaults = _.clone(account.account_defaults);
            clone.account_defaults.task_id = clone.task_id;
            this.initialize_content_group_clone_days(clone, records);
            return clone
        },
        initialize_content_group_clone_days: function(account, records) {
            var self = this;
            account.days = _.map(account.days, function(day)
            {
                var cloned_day = _.clone(day);
                cloned_day.lines = _.map(
                    _.filter(records, function(record) {
                        return date_to_str(day.day) == record.date;
                    }),
                    _.bind(
                        self.initialize_content_group_clone_record,
                        self, account
                    )
                );
                if(!cloned_day.lines.length)
                {
                    cloned_day.lines.unshift(_.extend(
                        {}, account.account_defaults,
                        {
                            name: self.description_line,
                            date: date_to_str(day.day),
                            unit_amount: 0,
                            account_id: account.account,
                        }
                    ));
                }
                return cloned_day;
            });
        },
        initialize_content_group_clone_record: function(account, record) {
            var result = _.clone(record);
            result.task_id = this._m2o_id(record.task_id);
            if(result.task_id != account.task_id)
            {
                result.unit_amount = 0;
                result.task_id = account.task_id;
            }
            return result;
        },
        initialize_content_group_by: function(record) {
            return _.str.sprintf(
                '%s-%s', this._m2o_id(record.account_id),
                this._m2o_id(record.task_id)
            );
        },
        _m2o_id: function(val) {
            // the || false is necessary because this can also be `undefined`
            // for legacy lines, which messes up qweb
            return val && val.length ? val[0] : (val || false);
        },
        init_add_account: function() {
            // add our field, attach handlers
            var self = this,
                result = this._super.apply(this, arguments);
            self.dfm.extend_field_desc({
                task: {
                    relation: "project.task",
                },
            });
            self.dfm.build_eval_context = self.proxy('_add_eval_context');
            self.task_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                attrs: {
                    name: "task",
                    type: "many2one",
                    domain: new instance.web.CompoundDomain(
                        '[("project_id.analytic_account_id", "=", account),' +
                        '("id", "not in", _all_task_ids)]'
                    ),
                },
            });
            self.account_m2o.node.attrs.domain = new instance.web.CompoundDomain(
                "[" +
                    "('type','in', ['normal', 'contract']), " +
                    "('state', '!=', 'close'), " +
                    "('use_timesheets', '=', True)" +
                "]"
            );
            self.task_m2o.insertBefore(
                self.$(".oe_timesheet_weekly_add_row td button")
            );
            return result;
        },
        _add_eval_context: function() {
            return new instance.web.CompoundContext({
                'account': this.account_m2o.get_value(),
                'task': this.task_m2o.get_value(),
                '_all_account_ids': _.pluck(this.accounts, 'account'),
                '_all_task_ids': _.pluck(this.accounts, 'task_id'),
            });
        },
        set: function(arg1, arg2, arg3) {
            // this is called by the click handler, we intercept setting
            // operations without a task id
            var self = this;
            if(arg1 && arg1.sheets && arg1.sheets.length && this.task_m2o)
            {
                // the new record is the last one
                var record = arg1.sheets[arg1.sheets.length - 1];
                // this happens when adding a row via the ui
                if(!record.task_id && self.task_m2o.get_value())
                {
                    record.task_id = self.task_m2o.get_value();
                }
            }
            return this._super.apply(this, arguments);
        },
        get_box: function(account, day_count) {
            return this._super.apply(this, arguments).filter(
                _.str.sprintf('[data-task="%s"]', account.task_id || 0)
            );
        },
        get_total: function(account) {
            return this._super.apply(this, arguments).filter(
                _.str.sprintf('[data-task="%s"]', account.task_id || 0)
            );
        },
    });
};
