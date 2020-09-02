odoo.define('allure_backend_theme_ent.ActivityMenu', function (require) {
    "use strict";

    var __themesDB = require('allure_backend_theme_ent.AllureWebThemes');

    var core = require('web.core');
    var session = require('web.session');
    var ActivityMenu = require('mail.systray.ActivityMenu');
    var QWeb = core.qweb;

    ActivityMenu.include({
        _fileExists: function (filename) {
            filename = filename.trim();
            var response = jQuery.ajax({
                url: filename,
                type: 'HEAD',
                async: false
            }).status;
            return (response == "200");
        },
        _getActivityData: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var userTheme = __themesDB.get_theme_config_by_uid(session.uid);
                var icon = userTheme.base_menu_icon;

                if (icon === '2d_icon') {
                    var iconPath = '/allure_backend_theme_ent/static/src/img/menu_2d/';
                } else if (icon === '3d_icon') {
                    var iconPath = '/allure_backend_theme_ent/static/src/img/menu/';
                };

                self._activities = _.map(self._activities, function (rec) {
                    var iconName = rec.icon.split('/')[1];
                    if (self._fileExists(iconPath + iconName + '.png')) {
                        rec.icon = iconPath + iconName + ".png"
                    } else {
                        rec.icon = iconPath + "/custom.png";
                        if (self._fileExists("/" + iconName + "/static/description/icon.png")) {
                            rec.icon = "/" + iconName + "/static/description/icon.png";
                        }
                    }
                    return rec;
                });

                self.menuType = icon;
                self.activityCounter = _.reduce(self._activities, function (total_count, p_data) {
                    return total_count + p_data.total_count || 0;
                }, 0);
                self.$('.o_notification_counter').text(self.activityCounter);
                self.$el.toggleClass('o_no_notification', !self.activityCounter);
            });
        },
    });
});
