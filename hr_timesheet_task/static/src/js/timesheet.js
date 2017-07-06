odoo.define('hr_timesheet_task.sheet', function (require) {
    'use strict';

    var core = require('web.core');
    var data = require('web.data');
    var form_common = require('web.form_common');
    var Model = require('web.DataModel');
    var time = require('web.time');
    var hr_timesheet_sheet = require('hr_timesheet_sheet.sheet');

    core.form_custom_registry.get('weekly_timesheet').include({
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
                res_model: 'project.project',
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
            var projects;
            var projects_by_tasks;
            var timesheet_lines;
            var task_names;
            var project_names;
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
                        if (typeof(el.project_id) === 'object')
                            el.project_id = el.project_id[0];
                        if (typeof(el.task_id) === 'object')
                            el.task_id = el.task_id[0];
                        return el;
                    }).value();

                // group by project
                projects = _.groupBy(timesheet_lines, function(el) {
                    return el.project_id;
                });

                // group by project and task
                projects_by_tasks = _.groupBy(timesheet_lines, function(el) {
                    return [el.project_id, el.task_id];
                });

                projects = _(projects_by_tasks).chain().map(function(lines, project_id_task_id) {
                    var project_id = lines[0].project_id;
                    var project_defaults = _.extend({}, default_get, (projects[project_id] || {}).value || {});
                    // group by days
                    project_id = (project_id === 'false')? false : Number(project_id);
                    var index = _.groupBy(lines, 'date');
                    var days = _.map(dates, function(date) {
                        var day = {day: date, lines: index[time.date_to_str(date)] || []};
                        // add line where we will insert/remove hours
                        var to_add = _.find(day.lines, function(line) { return line.name === self.description_line; });
                        if (to_add) {
                            day.lines = _.without(day.lines, to_add);
                            day.lines.unshift(to_add);
                        } else {
                            day.lines.unshift(_.extend(_.clone(project_defaults), {
                                name: self.description_line,
                                unit_amount: 0,
                                date: time.date_to_str(date),
                                project_id: project_id,
                                task_id: lines[0].task_id,
                            }));
                        }
                        return day;
                    });

                    var partner_id = undefined;

                    if(lines[0].partner_id){
                        if(parseInt(lines[0].partner_id, 10) == lines[0].partner_id){
                            partner_id = lines[0].partner_id;
                        } else {
                            partner_id = lines[0].partner_id[0];
                        }
                    }
                    return {project_task: project_id_task_id, project: project_id, days: days, project_defaults: project_defaults, task: lines[0].task_id, partner_id: partner_id};
                }).value();

                // we need the name_get of the analytic accounts
                return new Model('project.project').call('name_get', [_.pluck(projects, 'project'),
                    new data.CompoundContext()]).then(function(result) {
                    project_names = {};
                    _.each(result, function(el) {
                        project_names[el[0]] = el[1];
                    });
                    // we need the name_get of the tasks
                    return new Model('project.task').call('name_get', [_(projects).chain().pluck('task').filter(function(el) { return el; }).value(),
                        new data.CompoundContext()]).then(function(result) {
                        task_names = {};
                        _.each(result, function(el) {
                            task_names[el[0]] = el[1];
                        });
                        projects = _.sortBy(projects, function(el) {
                            return project_names[el.project];
                        });
                    });
                });
            })).then(function(result) {
                // we put all the gathered data in self, then we render
                self.dates = dates;
                self.projects = projects;
                self.project_names = project_names;
                self.task_names = task_names;
                self.default_get = default_get;
                //real rendering
                self.display_data();
            });
        },
        init_add_project: function() {
            var self = this;
            if (self.dfm) {
                self.dfm.destroy();
            }

            self.$('.oe_timesheet_weekly_add_row').show();
            self.dfm = new form_common.DefaultFieldManager(self);
            self.dfm.extend_field_desc({
                project: {
                    relation: 'project.project',
                },
                task: {
                    relation: 'project.task',
                },
            });
            var FieldMany2One = core.form_widget_registry.get('many2one');
            self.project_m2o = new FieldMany2One(self.dfm, {
                attrs: {
                    name: 'project',
                    type: 'many2one',
                    modifiers: '{"required": true}',
                },
            });

            self.task_m2o = new FieldMany2One(self.dfm, {
                attrs: {
                    name: 'task',
                    type: 'many2one',
                    domain: [
                        // at this moment, it is always an empty list
                        ['project_id','=',self.project_m2o.get_value()]
                    ],
                },
            });
            self.task_m2o.prependTo(this.$('.o_add_timesheet_line > div'));

            self.project_m2o.prependTo(this.$('.o_add_timesheet_line > div')).then(function() {
                self.project_m2o.$el.addClass('oe_edit_only');
            });

            self.project_m2o.$input.focusout(function(){
                self.onchange_project_id();
            });

            self.$(".oe_timesheet_button_add").click(function() {
                self.onclick_add_row_button();
            });
        },

        onclick_add_row_button: function(){
            var self = this;
            var id = self.project_m2o.get_value();
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
                project_id: id,
                task_id: task_id,
            }));

            self.set({sheets: ops});
            self.destroy_content();
        },

        onchange_project_id: function() {
            var self = this;
            var project_id = self.project_m2o.get_value();
            if (project_id === false) { return; }

            self.task_m2o.node.attrs.domain = [
                // show only tasks linked to the selected project
                ['project_id','=',project_id],
                // ignore tasks already in the timesheet
                ['id', 'not in', _.pluck(self.projects, 'task')],
            ];
            self.task_m2o.node.attrs.context = {'project_id': project_id};
            self.task_m2o.set_value(false);
            self.task_m2o.render_value();
        },

        get_box: function(project, day_count) {
            return this.$('[data-project-task="' + project.project_task + '"][data-day-count="' + day_count + '"]');
        },
    });
});


