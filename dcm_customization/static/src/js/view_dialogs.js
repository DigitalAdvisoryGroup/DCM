odoo.define('global_search_cr.view_dialogs', function (require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var GlobalSearchDialog = require('global_search_cr.Dialog');
var dom = require('web.dom');
var ListController = require('web.ListController');
var ListView = require('web.ListView');
var pyUtils = require('web.py_utils');
// var SearchView = require('web.SearchView');
var _t = core._t;

var ViewDialog = GlobalSearchDialog.extend({
    custom_events: _.extend({}, Dialog.prototype.custom_events, {
        push_state: '_onPushState',
        env_updated: function (event) {
            event.stopPropagation();
        },
    }),
    /**
     * @constructor
     * @param {Widget} parent
     * @param {options} [options]
     * @param {string} [options.dialogClass=o_act_window]
     * @param {string} [options.res_model] the model of the record(s) to open
     * @param {any[]} [options.domain]
     * @param {Object} [options.context]
     */
    init: function (parent, options) {
        options = options || {};
        options.dialogClass = options.dialogClass || '' + ' o_act_window';
        this._super(parent, $.extend(true, {}, options));

        this.res_model = options.res_model.split('-')[0] || null;
        this.domain = options.domain || [];
        this.context = options.context || {};
        this.options = _.extend(this.options || {}, options || {});

        // FIXME: remove this once a dataset won't be necessary anymore to interact
        // with data_manager and instantiate views
        this.dataset = new data.DataSet(this, this.res_model, this.context);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * We stop all push_state events from bubbling up.  It would be weird to
     * change the url because a dialog opened.
     *
     * @param {OdooEvent} event
     */
    _onPushState: function (event) {
        event.stopPropagation();
    }
});

var SelectCreateListController = ListController.extend({
    // Override the ListView to handle the custom events 'open_record' (triggered when clicking on a
    // row of the list) such that it triggers up 'select_record' with its res_id.
    custom_events: _.extend({}, ListController.prototype.custom_events, {
        open_record: function (event) {
            var selectedRecord = this.model.get(event.data.id);
            this.trigger_up('select_record', {
                id: selectedRecord.res_id,
                display_name: selectedRecord.data.display_name,
                model_name: $(event.target.$el).parent().prev().attr('id')
            });
        }
    })
});

var SelectCreateDialog = ViewDialog.extend({
    custom_events: _.extend({}, ViewDialog.prototype.custom_events, {
        select_record: function (event) {
            var self = this;
            var form_view_id = self.options.models_data[event.data.model_name]['form_view_id']
            // Set Options
            this.options.res_id = event.data.id;
            this.options.readonly = true;
            this.res_model = event.target.modelName.split('-')[0] || this.res_model.split('-')[0];
            this.options.res_model = event.target.modelName.split('-')[0] || this.res_model.split('-')[0];
            var views = [[ form_view_id || false, 'form']];

            self._rpc({
                model: 'global.search',
                method: 'get_app_data',
                args: [self.options.res_model],
            })
            .then(function (res) {
                return self.do_action({
                    type: 'ir.actions.act_window',
                    name: self.options.models_data[self.options.res_model]['label'],
                    res_model: self.options.res_model.split('-')[0],
                    views: views,
                    search_view_id: [false],
                    res_id: self.options.res_id,
                }, {clear_breadcrumbs: true}).then(function () {
                    // Change Application Section
                    core.bus.trigger('change_menu_section', res[self.options.res_model]['menu_id']);
                    self.close();
                });
            });
        },
        selection_changed: function (event) {
            event.stopPropagation();
            this.$footer.find(".o_select_button").prop('disabled', !event.data.selection.length);
        },
        search: function (event) {
            var self = this;
            event.stopPropagation(); // prevent this event from bubbling up to the view manager
            var d = event.data;
            _.each(this.controllers, function(controller){
                if (event.target && event.target.dataset && event.target.dataset.model == controller.modelName){
                    // Update Context & Domain TODO: Need to include Groupbys
                    self.options.models_data[controller.modelName]['context'] = 
                        pyUtils.eval_domains_and_contexts({
                            domains: [],
                            contexts: d.contexts
                        }).context;
                    self.options.models_data[controller.modelName]['domain'] = d.domains;
                    
                    var searchData = self._process_search_data(controller.modelName, d.domains, d.contexts, d.groupbys);
                    controller.reload(searchData);
                };
            });
        },
        get_controller_context: '_onGetControllerContext',
    }),

    /**
     * options:
     * - initial_ids
     * - initial_view: form or search (default search)
     * - list_view_options: dict of options to pass to the List View
     * - on_selected: optional callback to execute when records are selected
     * - disable_multiple_selection: true to allow create/select multiple records
     */
    init: function () {
        this._super.apply(this, arguments);
        _.defaults(this.options, { initial_view: 'search' });
        this.on_selected = this.options.on_selected || (function () {});
        this.initial_ids = this.options.initial_ids;
        this.options.res_id = false;
        this.controllers = [];
    },

    open: function () {
        var self = this;
        var user_context = this.getSession().user_context;

        var _super = this._super.bind(this);
        var context = pyUtils.eval_domains_and_contexts({
            domains: [],
            contexts: [user_context, this.context]
        }).context;
        var search_defaults = {};
        _.each(context, function (value_, key) {
            var match = /^search_default_(.*)$/.exec(key);
            if (match) {
                search_defaults[match[1]] = value_;
            }
        });

        // Fragment
        var fragment = document.createDocumentFragment();
        self.loadViews(self.dataset.model.split('-')[0], self.dataset.context, [[ self.options.models_data[self.dataset.model]['list_view_id'] || false, 'list'], [false, 'search']], {})
            .then(self.setup.bind(self, search_defaults, self.dataset.model.split('-')[0], fragment))
            .then(function (fragmentres) {
                self.opened().then(function () {
                    dom.append(self.$el, fragmentres, {
                        callbacks: [{widget: self.list_controller}],
                        in_DOM: true,
                    });
                    self.set_buttons(self.__buttons);
                });
                _super();
            });
        
        return this;
    },

    setup: function (search_defaults, model, fragment, fields_views) {
        var self = this;
        var fragment = fragment;
        var searchDef = $.Deferred();
        _.each(this.options.models, function(datamodel) {
            // Compute Default Filters
            var user_context = self.getSession().user_context;
            var context = pyUtils.eval_domains_and_contexts({
                domains: [],
                contexts: [user_context, self.options.models_data[datamodel]['context']]
            }).context;

            var search_defaults = {};
            _.each(context, function (value_, key) {
                var match = /^search_default_(.*)$/.exec(key);
                if (match) {
                    search_defaults[match[1]] = value_;
                }
            });
            // Search Controller & List Views
            var $model_search = $('<div res_model=' + datamodel.split('-')[0] + '/>').addClass('').appendTo(fragment);
            var $list_label = $('<div res_model=' + datamodel.split('-')[0] + '></div>').addClass('o_list_label').appendTo($model_search);
            var $list_label_btn = $('<span>'+ self.options.models_data[datamodel]["label"] +'</span>').addClass('o_list_label_btn').appendTo($list_label);
            
            // Open Model List Page
            $list_label_btn.click(function(e) {
                e.preventDefault();
                var views = [[self.options.models_data[datamodel]['list_view_id'] || false, 'list'], [self.options.models_data[datamodel]['form_view_id'] || false, 'form']];
                var action_domain = self.options.models_data[datamodel]['domain'];
                var action_context = self.options.models_data[datamodel]['context'];
                self._rpc({
                    model: 'global.search',
                    method: 'get_app_data',
                    args: [datamodel],
                })
                .then(function (res) {
                    return self.do_action({
                        type: 'ir.actions.act_window',
                        name: self.options.models_data[datamodel]['label'],
                        res_model: datamodel.split('-')[0],
                        views: views,
                        search_view_id: [false],
                        context: action_context,
                        domain: action_domain,
                    }, {clear_breadcrumbs: true}).then(function () {
                        // Change Application Section
                        core.bus.trigger('change_menu_section', res[datamodel]['menu_id']);
                        self.close();
                    });
                });
            });

            var $header = $('<div id=' + datamodel + '/>').addClass('o_modal_header global_search_modal_header '+ datamodel +'').appendTo($model_search);
            var $pager = $('<div t-att-data-id=' + datamodel.split('-')[0] + '/>').addClass('o_pager '+ datamodel.split('-')[0] +'').appendTo($header);
            var options = {
                $buttons: $('<div t-att-data-res_model=' + datamodel + '/>').addClass('o_search_options').appendTo($header),
                search_defaults: search_defaults,
                action: {id: self.options.models_data[datamodel]['action_id']},
            };

            self.loadViews(datamodel.split('-')[0], self.dataset.context, [[self.options.models_data[datamodel]['list_view_id'] || false, 'list'], [false, 'search']], {'action_id':self.options.models_data[datamodel]['action_id']}).then(function(cust_fields_views){

                self.dataset = new data.DataSet(self, datamodel.split('-')[0], self.context);

                // Set the dialog's header and its search view
                var searchview = new SearchView(self, self.dataset, cust_fields_views.search, options);
                searchview.prependTo($header).done(function () {
                    var d = searchview.build_search_data();
                    if (self.initial_ids) {
                        d.domains.push([["id", "in", self.initial_ids]]);
                        self.initial_ids = undefined;
                    }
                    // Push Search Domain
                    d.domains.push(self.options.models_data[datamodel]['domain']);
                    d.contexts.push(self.options.models_data[datamodel]['context'] || {});
                    var searchData = self._process_search_data(datamodel, d.domains, d.contexts, d.groupbys);
                    searchDef.resolve(searchData);
                });

                $.when(searchDef).then(function (searchResult) {
                    // Update Global Search Actions reference in Context
                    searchResult.context['global_search_actions'] = true;
                    // Set the list view
                    var listView = new ListView(cust_fields_views.list, _.extend({
                        context: searchResult.context,
                        domain: self.options.models_data[datamodel]['domain'],
                        groupBy: searchResult.groupBy,
                        modelName: datamodel.split('-')[0],
                        hasSelectors: !self.options.disable_multiple_selection,
                        readonly: true,
                    }, self.options.list_view_options));
                    listView.setController(SelectCreateListController);
                    listView.getController(self);
                    return listView.getController(self);

                }).then(function (controller) {
                    self.list_controller = controller;
                    // Prepare Controllers List
                    self.controllers.push(controller);
                    // Set the dialog's buttons
                    self.__buttons = [{
                        text: _t("Close"),
                        classes: "btn-default o_form_button_cancel",
                        close: true,
                    }];
                    // Append List Controller in Model Search Container
                    self.list_controller.appendTo($model_search);
                    return self.list_controller;
                }).then(function () {
                    searchview.toggle_visibility(true);
                    self.list_controller.do_show();
                    self.list_controller.renderPager($pager);
                    return fragment;
                }).then(function(fr){
                    self.opened().then(function () {
                        dom.append(self.$el, fr, {
                            callbacks: [{widget: self.list_controller}],
                            in_DOM: true,
                        });
                        self.set_buttons(self.__buttons);
                    });
                });
            });
        });
    },

    _process_search_data: function (res_model, domains, contexts, groupbys) {
        var results = pyUtils.eval_domains_and_contexts({
            domains: [this.domain].concat(domains),
            contexts: [this.context].concat(contexts),
            group_by_seq: groupbys || [],
            eval_context: this.getSession().user_context,
        });
        var context = _.omit(results.context, function (value, key) { return key.indexOf('search_default_') === 0; });

        // Update New Contexts & Domains
        this.options.models_data[res_model]['context'] = context;
        this.options.models_data[res_model]['domain'] = results.domain;
        
        return {
            context: context,
            domain: results.domain,
            groupBy: results.group_by,
        };
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Handles a context request: provides to the caller the context of the
     * list controller.
     *
     * @private
     * @param {OdooEvent} ev
     * @param {function} ev.data.callback used to send the requested context
     */
    _onGetControllerContext: function (ev) {
        ev.stopPropagation();
        var context = this.list_controller.getContext();
        ev.data.callback(context);
    }
});

return {
    SelectCreateDialog: SelectCreateDialog,
};

});
