odoo.define('dcm_customization.dashboard_chart_preview_social_group', function (require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var QWeb = core.qweb;

    var dashboard_chart_preview_social_group = AbstractField.extend({
        supportedFieldTypes: ['char'],
        resetOnAnyFieldChange: true,
//        cssLibs:[
//            '/dcm_customization/static/src/css/highchart_dashboard.css',
//        ],
        start: function () {
            var self = this;
            return this._super();
        },

        hexToRgb: function(hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        },

        _render: function () {
            var self = this;
            var chart_view = self.$el.append($(QWeb.render('highchart_dashboard_chart_form_view_preivew')));

            Promise.all([chart_view]).then(function () {
                self.$el.find('#chart_container').html('');
                    self.$el.find('#chart_container').css({"height": "500px"});
                    var options = JSON.parse(self.recordData.chart_data);
                    if (options.chart){
                        setTimeout(function(){ Highcharts.chart(options); }, 300);
                    }
            });
        },
    });

    registry.add('dashboard_chart_preview_social_group', dashboard_chart_preview_social_group);
    return {
        dashboard_chart_preview_social_group: dashboard_chart_preview_social_group,
    };

});