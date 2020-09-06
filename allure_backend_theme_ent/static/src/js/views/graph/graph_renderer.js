odoo.define('allure_backend_theme_ent.GraphRenderer', function (require) {
    "use strict";

    var __themesDB = require('allure_backend_theme_ent.AllureWebThemes');

    var GraphRenderer = require('web.GraphRenderer');
    var COLORS = ["#1f77b4", "#ff7f0e", "#aec7e8", "#ffbb78", "#2ca02c", "#98df8a", "#d62728",
        "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2",
        "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"];
    var COLOR_NB = COLORS.length;
    var session = require('web.session');

    return GraphRenderer.include({
        init: function (parent, state, params) {
            this.userTheme = __themesDB.get_theme_config_by_uid(session.uid);
            this._super.apply(this, arguments);
        },
        willStart: function () {
            var self = this;

            var invertColor = function (hexTripletColor) {
                var color = hexTripletColor;
                color = color.substring(1); // remove #
                color = parseInt(color, 16); // convert to integer
                color = 0xFFFFFF ^ color; // invert three bytes
                color = color.toString(16); // convert to hex
                color = ("000000" + color).slice(-6); // pad with leading zeros
                color = "#" + color; // prepend #
                return color;
            }

            return this._super.apply(this, arguments).then(function () {
                var _isValidHex = function(hexString) { return /^#[0-9A-F]{6}$/i.test(hexString); };
                var THEME_COLORS = _.uniq(_.filter(_.values(self.userTheme), function(value) { return _isValidHex(value); }));
                var ALL_COLORS = _.union(THEME_COLORS, COLORS);

                if (self.userTheme.mode === "night_mode_on") {
                    var _invertCOLORs = [];
                    _.each(ALL_COLORS, function(hexColor) {
                        _invertCOLORs.push(invertColor(hexColor));
                    });
                    COLORS = _invertCOLORs;
                } else {
                    COLORS = ALL_COLORS;
                };

                COLOR_NB = COLORS.length;
            });
        },
        _getColor: function (index) {
            return COLORS[index % COLOR_NB];
        },
        _getLegendOptions: function (datasetsCount) {
            var options = this._super.apply(this, arguments);
            if (_.isEmpty(options) || this.userTheme.mode !== "night_mode_on") {
                return options;
            }
            _.each(_.keys(options), function() {
                if (_.has(options || {}, "labels")) {
                    _.extend(options.labels, {}, {fontColor: 'white'});
                }
            });
            return options;
        },
        _getScaleOptions: function () {
            var options =  this._super.apply(this, arguments);
            if (_.isEmpty(options) || this.userTheme.mode !== "night_mode_on") {
                return options;
            }
            _.each(_.keys(options), function(key) {
                if (_.has(options[key][0] || {}, "ticks")) {
                    _.extend(options[key][0].ticks, {}, {fontColor: 'white'});
                }
                if (_.has(options[key][0] || {}, "scaleLabel")) {
                    _.extend(options[key][0].scaleLabel, {}, {fontColor: 'white'});
                }
                if (_.has(options || {}, 'xAxes')) {
                    _.extend(options[key][0] ,{}, {gridLines: {zeroLineColor:'white', color: '#636363'}});
                }
            });
            return options;
        },
    });
});
