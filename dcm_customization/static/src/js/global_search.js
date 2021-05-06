odoo.define('global_search_cr.GlobalSearch', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var SystrayMenu = require('web.SystrayMenu');
var view_dialogs = require('global_search_cr.view_dialogs');
var ListView = require('web.ListView');
var SystrayMenu = require('web.SystrayMenu');
var rpc = require('web.rpc');
var QWeb = core.qweb;
var _t = core._t;

// List View
ListView.include({
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        // Allow 20 records in Global Search List View 
        if (this.loadParams && this.loadParams.context && this.loadParams.context.global_search_actions){
            this.loadParams.limit = 20;
        };
    }
});

var GlobalSearchMenu = Widget.extend({
    template:'GlobalSearch.input',
    sequence: 200,

    events: {
        "click": "_onGlobalSearchClick",
        "click .o_global_search_preview": "_onSearchRecordClick",
        "click .o_category_header": "_onCategoryClick",
        "click input.o_menu_global_search_input": function(ev){
            ev.stopPropagation();
        },
        "click .o_view_detailed_search": function(e){
            var self = this;
             // Toggle Dropdown
            $('.o_global_search_systray').toggleClass('show');
            $('.o_mail_navbar_global_dropdown').toggleClass('show');

            var value = $('input.o_menu_global_search_input').val();
            this._rpc({
                model: 'global.search',
                method: 'get_records',
                args: [value],
                context:self.getSession().user_context
            })
            .then(function(result) {
                self.search_models = Object.keys(result);
                self.search_records = result;
                self.$global_search_preview.html(QWeb.render('GlobalSearch', {
                    search_models : self.search_models,
                    records : self.search_records,
                }));
                self._addSearchboard(value, result);
            });
        },

        'keydown input.o_menu_global_search_input': function(e) {
            var self = this;
            // Search Records on Enter
            if (e.which == 13 && !e.ctrlKey && e.target.value || e.keyCode == 13 && !e.ctrlKey && e.target.value) {
                this.update({search: e.target.value, focus: 1});
                // Open Dropdown Window to display Results
                if (!this._isOpen()) {
                    $('.o_global_search_systray').toggleClass('show');
                    $('.o_mail_navbar_global_dropdown').toggleClass('show');
                }
            }else if (e.which == 13 && e.ctrlKey && e.target.value || e.keyCode == 13 && e.ctrlKey && e.target.value) {

                this._rpc({
                    model: 'global.search',
                    method: 'get_records',
                    args: [e.target.value],
                    context:self.getSession().user_context
                })
                .then(function(result) {
                    self.search_models = Object.keys(result);
                    self.search_records = result;
                    self.$global_search_preview.html(QWeb.render('GlobalSearch', {
                        search_models : self.search_models,
                        records : self.search_records,
                    }));
                    self._addSearchboard(e.target.value, result);
                });

            };
        },
        'input input.o_menu_global_search_input': function(e) {
            // Clear Results when Empty
            if (!e.target.value) {
                this.update({search: e.target.value, focus: 1});
            };
        },
    },

    update: function(data) {
        var self = this;
        if (data) {
            this._rpc({
                model: 'global.search',
                method: 'get_records',
                args: [data.search],
                context:self.getSession().user_context
            })
            .then(function(result) {
                self.search_models = Object.keys(result);
                self.search_records = result;
                self.$global_search_preview.html(QWeb.render('GlobalSearch', {
                    search_models : self.search_models,
                    records : self.search_records,
                }));
            });
        }
    },

    start: function () {
        this.$global_search_preview = this.$('.o_mail_navbar_global_search_dropdown');
        this._updateGlobalSearch();
        return this._super();
    },

    // Open Search View
    _addSearchboard: function (search_content, model_data) {
        var self = this;
        var context = this.getSession().user_context;

        return self._rpc({
            model: 'global.search',
            method: 'open_in_dashboard',
            args: [search_content, model_data],
        })
        .then(function (r) {
            if (r) {
                var models = [];
                _.each(r, function (datas, model) {
                    models.push(model);
                });
                if (models.length != 0){
                    new view_dialogs.SelectCreateDialog(self, _.extend({}, self.nodeOptions, {
                        res_model: models && models[0],
                        domain: [],
                        context: context,
                        models: models,
                        models_data: r,
                        title: _t('Global Search'),
                        initial_ids: undefined,
                        initial_view: 'search',
                        disable_multiple_selection: true,
                    })).open();
                };
            };
        });
    },

    _isOpen: function () {
        return this.$el.hasClass('show');
    },

    /**
     * Update(render) Global Search system tray view.
     * @private
     */
    // Global Search
    _updateGlobalSearch: function () {
        var self = this;

        self.$global_search_preview.html(QWeb.render('GlobalSearch', {
            records : self.search_records || [],
            search_models : self.search_models || [],
        }));
    },

    // Handlers

    /**
     * Redirect to particular model view
     * @private
     * @param {MouseEvent} event
     */
    _onSearchRecordClick: function (event) {
        var self = this;
        // Toggle Dropdown
        $('.o_global_search_systray').toggleClass('show');
        $('.o_mail_navbar_global_dropdown').toggleClass('show');

        var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
        var context = {};
        if (data && data.form_view_id){
            var views = [[data.form_view_id, 'form']];
        }else{
            var views = [[false, 'form']];
        };
        self._rpc({
            model: 'global.search',
            method: 'get_app_data',
            args: [data.res_model],
        })
        .then(function (res) {
            return self.do_action({
                type: 'ir.actions.act_window',
                name: data.res_header,
                res_model:  data.res_model.split('-')[0],
                views: views,
                search_view_id: [false],
                res_id: data.res_id,
                context:context,
            }, {clear_breadcrumbs: true}).then(function () {
                // Change Application Section
                core.bus.trigger('change_menu_section', res[data.res_model]['menu_id']);
            });
        });
    },
    _get_context(input, data){
        var context = {};
        // Prepare Context
        if (input && data.res_model.split('-')[0] != 'res.partner' && input[0] && input[0].value){
            var context = {'search_default_name': input[0].value};
        }else if(input && data.res_model.split('-')[0] == 'res.partner' && input[0] && input[0].value){
            var context = {'search_default_ref': input[0].value};
        };
        return context
    },
    // Open all searched records
    _onCategoryClick: function (event) {
        var self = this;
        // Toggle Dropdown
        $('.o_global_search_systray').toggleClass('show');
        $('.o_mail_navbar_global_dropdown').toggleClass('show');

        var input = $('input.o_menu_global_search_input');
        var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
        var context = self._get_context(input, data)
        // Prepare Views List
        if (data && data.list_view_id){
            var views = [[data.list_view_id, 'list'],[false, 'kanban'], [data.form_view_id, 'form']];
        }
        else if (data && data.kanban_view_id){
            var views = [[false, 'list'], [data.kanban_view_id, 'kanban'], [false, 'form']];
        }else{
            var views = [[false, 'list'], [false, 'kanban'], [false, 'form']];
        };
        self._rpc({
            model: 'global.search',
            method: 'get_app_data',
            args: [data.res_model],
        })
        .then(function (res) {
           var do_action_data = {
                type: 'ir.actions.act_window',
                name: data.res_header,
                res_model: data.res_model.split('-')[0],
                views: views,
                search_view_id: [false],
                context: context,
            }
            if(res[data.res_model]['domain']){
                do_action_data['domain'] = res[data.res_model]['domain']
            }
            return self.do_action(do_action_data, {clear_breadcrumbs: true}).then(function () {
                // Change Application Section
                core.bus.trigger('change_menu_section', res[data.res_model]['menu_id']);
            });
        });
    },

    /**
     * When menu clicked update Global Search preview
     */
    _onGlobalSearchClick: function () {
        if (!this._isOpen()) {
            this._updateGlobalSearch();
        }
    }
});

rpc.query({
    model: 'res.users',
    method: 'get_global_search_right',
    args: [[],[]],
}).then(has_right => {
    if(has_right)
    SystrayMenu.Items.push(GlobalSearchMenu);
});


return GlobalSearchMenu





});