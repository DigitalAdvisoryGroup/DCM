odoo.define('allure_studio_ent.FormEditor', function (require) {
    "use strict";

    var FormEditorHook = require('web_studio.FormEditorHook');
    var FormEditor = require('web_studio.FormEditor');
    var Menu = require('web_enterprise.Menu');

    FormEditor.include({
        _renderTabHeader_new: function (page, page_id) {
            var self = this;
            var $result = this._super.apply(this, arguments);
            $result.attr('data-node-id', this.node_id++);
            this.setSelectable($result);
            $result.click(function (event) {
                event.preventDefault();
                if (!self.silent) {
                    self.selected_node_id = $result.data('node-id');
                    self.trigger_up('node_clicked', {node: page});
                }
            });
            return $result;
        },
        _renderTagNotebook: function (node) {
            var self = this;
            var $result = this._super.apply(this, arguments);

            var $addTag = $('<li>', {class: 'nav-item oe_new_add'})
                .append('<a href="#" class="nav-link border"><i class="fa fa-plus-square"/></a>');
            $addTag.click(function (event) {
                event.preventDefault();
                event.stopPropagation();
                self.trigger_up('view_change', {
                    type: 'add',
                    structure: 'page',
                    position: 'inside',
                    node: node,
                });
            });
            $result.find('ul.panel-ul').append($addTag);

            var formEditorHook = this._renderHook(node, 'after', '', 'afterNotebook');
            formEditorHook.appendTo($result);
            return $result;
        },
    });

    Menu.include({
        switchMode: function (mode) {
            var self = this;
            this._super.apply(this, arguments);
            if (!mode) {
                if (this.themeData && this.themeData.base_menu === 'base_menu') {
                    this.$detached_systray.appendTo('.oe_menu_base_layout');
                } else {
                    this.$detached_systray.appendTo('.o_toggle_menu li');
                }
                if (this.studio_menu) {
                    this.studio_menu.destroy();
                    this.studio_menu = undefined;
                }
            }
        },
    });
});