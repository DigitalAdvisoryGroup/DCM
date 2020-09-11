odoo.define('mail_theme_custom_cr.kanbancontroller', function (require) {
    "use strict";

    var KanbanRecord = require('web.KanbanRecord');
    var Massmailing = require('mass_mailing.FieldHtml');
    var config = require('web.config');
    var core = require('web.core');


    Massmailing.include({
        _onSnippetsLoaded: function (ev) {
            var self = this;
            // if (!this.$content) {
            //     this.snippetsLoaded = ev;
            //     return;
            // }
            var $snippetsSideBar = ev.data;
            var $themes = $snippetsSideBar.find("#email_designer_themes").children();
            var $snippets = $snippetsSideBar.find(".oe_snippet");
            var $snippets_menu = $snippetsSideBar.find("#snippets_menu");
    
            if (config.device.isMobile) {
                $snippetsSideBar.hide();
                this.$content.attr('style', 'padding-left: 0px !important');
            }
    
            if ($themes.length === 0) {
                return;
            }
    
            /**
             * Initialize theme parameters.
             */
            this._allClasses = "";
            var themesParams = _.map($themes, function (theme) {
                var $theme = $(theme);
                var name = $theme.data("name");
                var classname = "o_" + name + "_theme";
                self._allClasses += " " + classname;
                var imagesInfo = _.defaults($theme.data("imagesInfo") || {}, {
                    all: {}
                });
                _.each(imagesInfo, function (info) {
                    info = _.defaults(info, imagesInfo.all, {
                        module: "mass_mailing",
                        format: "jpg"
                    });
                });
                return {
                    name: name,
                    className: classname || "",
                    img: $theme.data("img") || "",
                    template: $theme.html().trim(),
                    nowrap: !!$theme.data('nowrap'),
                    get_image_info: function (filename) {
                        if (imagesInfo[filename]) {
                            return imagesInfo[filename];
                        }
                        return imagesInfo.all;
                    }
                };
            });
            $themes.parent().remove();
    
            /**
             * Create theme selection screen and check if it must be forced opened.
             * Reforce it opened if the last snippet is removed.
             */
            var $dropdown = $(core.qweb.render("mass_mailing.theme_selector", {
                themes: themesParams
            })).dropdown();
    
            // var firstChoice = this._checkIfMustForceThemeChoice();
    
            /**
             * Add proposition to install enterprise themes if not installed.
             */
            var $mail_themes_upgrade = $dropdown.find(".o_mass_mailing_themes_upgrade");
            $mail_themes_upgrade.on("click", function (e) {
                e.stopImmediatePropagation();
                e.preventDefault();
                self.do_action("mass_mailing.action_mass_mailing_configuration");
            });
    
            /**
             * Switch theme when a theme button is hovered. Confirm change if the theme button
             * is pressed.
             */
            var selectedTheme = false;
            $dropdown.on("mouseleave", ".dropdown-item", function (e) {
                self._switchThemes(false, selectedTheme);
            });
            $dropdown.on("click", '[data-toggle="dropdown"]', function (e) {
                var $menu = $dropdown.find('.dropdown-menu');
                var isVisible = $menu.hasClass('show');
                if (isVisible) {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    $menu.removeClass('show');
                }
            });
            $dropdown.insertAfter($snippets_menu);
        },
    });

    KanbanRecord.include({
        
        _openRecord: function () {
            if (this.modelName === "mail.themes") {
                var self = this;
                this._rpc({
                    method: 'set_theme_to_mailing',
                    model: 'mailing.mailing',
                    args: [this.state.context.mass_mailing_id],
                    context:{
                        'theme_id':self.id
                    }
                }).then(function (result) {
                    // debugger
                    self.do_action(result);
                });
            } else {
                this._super.apply(this, arguments);
            }
        },
    });


    
});

