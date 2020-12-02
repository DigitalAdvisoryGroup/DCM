odoo.define('highchart_dashboard.ListImportDashboardButton', function (require) {
"use strict";

var BasicController = require('web.BasicController');
var Context = require('web.Context');
var core = require('web.core');
var Dialog = require('web.Dialog');
var Domain = require('web.Domain');
var view_dialogs = require('web.view_dialogs');
var viewUtils = require('web.viewUtils');

var _t = core._t;
var qweb = core.qweb;

var ListController = require('web.ListController');

ListController.include({

    renderButtons: function ($node) {
        var self = this;
        this._super.apply(this, arguments);
        if (this.$buttons) {
            this.$buttons.click(this.on_import_dashboard_click.bind(this));
        }
    },

    on_import_dashboard_click: function () {
        var self =this;
        var state = this.model.get(this.handle, {raw: true});
        var $target = $(event.target);
        if ($target.hasClass('o_button_dashboard_import')) {
            self.do_action({
                name: _t('Import Dashboard'),
                type:'ir.actions.act_window',
                res_model: 'import.dashboard.wizard',
                views: [[false, 'form']],
                view_type: 'form',
                view_mode: 'form',
                target: 'new',
            });
        }
    },
});

});
