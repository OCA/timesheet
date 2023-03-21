/* Copyright 2021 Hunki Enterprises BV
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('hr_timesheet_portal', function(require){
    "use strict";

    var sAnimation = require('website.content.snippets.animation'),
        rpc = require('web.rpc'),
        core = require('web.core'),
        _t = core._t;

    sAnimation.registry.hr_timesheet_portal = sAnimation.Class.extend({
        selector: 'div.hr_timesheet_portal',
        events: {
            'click h5': '_onclick_add',
            'click tr[data-line-id]:not(.edit)': '_onclick_edit',
            'click i.fa-remove': '_onclick_delete',
            'click button.submit': '_onclick_submit',
            'submit form': '_onclick_submit',
            'click button.cancel': '_reload_timesheet',
        },

        start: function (editable_mode) {
            if (editable_mode) {
                this.stop();
                return;
            }
        },

        _onclick_delete: function (e) {
            e.stopPropagation();
            rpc.query({
                model: 'account.analytic.line',
                method: 'unlink',
                args: [[jQuery(e.currentTarget).parents('tr').data('line-id')]]
            })
            .done(this.proxy('_reload_timesheet'))
            .fail(this.proxy('_display_failure'));
        },

        _onclick_add: function (e) {
            var self = this;
            return rpc.query({
                model: 'account.analytic.line',
                method: 'create',
                args: [{
                    user_id: this.getSession().user_id,
                    account_id: this.$el.data('account-id'),
                    project_id: this.$el.data('project-id'),
                    task_id: this.$el.data('task-id'),
                    unit_amount: 0,
                    name: '/',
                }],
            })
            .done(function (line_id) {
                return self._reload_timesheet().then(function () {
                    setTimeout(self._edit_line.bind(self, line_id), 0);
                });
            })
            .fail(this.proxy('_display_failure'));
        },

        _onclick_edit: function (e) {
            return this._edit_line(jQuery(e.target).parents('tr').data('line-id'));
        },

        _onclick_submit: function (e) {
            e.preventDefault();
            var $tr = jQuery(e.target).parents('tr'),
                data = _.object(_.map($tr.find('form').serializeArray(), function(a) {
                    return [a.name, a.value]
                }));
            return rpc.query({
                model: 'account.analytic.line',
                method: 'write',
                args: [$tr.data('line-id'), data],
            })
            .done(this.proxy('_reload_timesheet'))
            .fail(this.proxy('_display_failure'));

        },

        _reload_timesheet: function () {
            var self = this;
            this.$el.children('div.alert').remove();
            return $.ajax({
                dataType: 'html',
            }).then(function (data) {
                var timesheets = _.filter(jQuery.parseHTML(data), function (element) {
                    return jQuery(element).find('div.hr_timesheet_portal').length > 0;
                }), $tbody = jQuery(timesheets).find('tbody');
                return self.$('tbody').replaceWith($tbody);
            });
        },

        _display_failure: function (error) {
            this.$el.prepend(jQuery('<div class="alert alert-danger">').text(error.data.message));
            this.$el.prepend(jQuery('<div class="alert alert-danger">').text(error.message));
        },

        _edit_line (line_id) {
            var $line = this.$(_.str.sprintf('tr[data-line-id=%s]', line_id)),
                $edit_line = $line.clone();
            this.$('tbody tr.edit').remove();
            this.$('tbody tr').show();
            $line.before($edit_line)
            $edit_line.children('[data-field-name]').each(function () {
                var $this = jQuery(this),
                    $input = jQuery('<input>', {
                        class: 'form-control',
                        type: $this.data('field-type') || 'text',
                        value: $this.data('field-value') || $this.text(),
                        form: 'hr_timesheet_portal_form',
                        name: $this.data('field-name'),
                    });
                $this.empty().append($input);
            });
            $edit_line.addClass('edit');
            var $form = jQuery('<form>', {
                id: 'hr_timesheet_portal_form',
            }), $submit = jQuery('<button class="btn btn-primary submit">'),
                $cancel = jQuery('<button class="btn cancel" type="reset">');
            $edit_line.children('td:last-child').append($form);
            $submit.text(_t('Submit'));
            $cancel.text(_t('Cancel'));
            $form.append($submit, $cancel);
            $edit_line.find('input:first').focus();
            $line.hide();
        },
    });

    return {animation: hr_timesheet_portal};

});
