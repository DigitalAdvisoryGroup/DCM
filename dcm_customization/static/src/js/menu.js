odoo.define('global_search_cr.Menu', function (require) {
"use strict";

var config = require('web.config');
var Menu = require('web_enterprise.Menu');

Menu.include({
    _handle_extra_items: function () {
        if (!this.$el.is(":visible"))
            return;

        if (this.$extraItemsToggle) {
            this.$extraItemsToggle.find("> ul > *").appendTo(this.$section_placeholder);
            this.$extraItemsToggle.remove();
        }
        if (config.device.size_class < config.device.SIZES.SM) {
            return;
        }
        var width = this.$el.width();
        var menuItemWidth = this.$section_placeholder.outerWidth(true);
        // Add 120px for Planner Block
        var othersWidth = this.$menu_toggle.outerWidth(true) + this.$menu_brand_placeholder.outerWidth(true) + this.systray_menu.$el.outerWidth(true) + 120;
        
        if (width < menuItemWidth + othersWidth) {
            var $items = this.$section_placeholder.children();
            var nbItems = $items.length;
            menuItemWidth += 46; // @odoo-navbar-height (width of the "+" button)
            do {
                nbItems--;
                menuItemWidth -= $items.eq(nbItems).outerWidth(true);
            } while (width < menuItemWidth + othersWidth);

            var $extraItems = $items.slice(nbItems).detach();
            this.$extraItemsToggle = $("<li/>", {"class": "o_extra_menu_items"});
            this.$extraItemsToggle.append($("<a/>", {href: "#", "class": "dropdown-toggle fa fa-plus", "data-toggle": "dropdown"}));
            this.$extraItemsToggle.append($("<ul/>", {"class": "dropdown-menu"}).append($extraItems));
            this.$extraItemsToggle.appendTo(this.$section_placeholder);
        }
    }
});

});
