odoo.define('highchart_dashboard.dashboard_chart_preview', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var utils = require('web.utils');
    var config = require('web.config');
    var fieldUtils = require('web.field_utils');

    var QWeb = core.qweb;

    var DashboardChartPreview = AbstractField.extend({
        supportedFieldTypes: ['char'],
        resetOnAnyFieldChange: true,

        jsLibs:[
            '/highchart_dashboard/static/lib/js/highcharts.js',
            '/highchart_dashboard/static/lib/js/highcharts-more.js',
            '/highchart_dashboard/static/lib/js/exporting.js',
            '/highchart_dashboard/static/lib/js/offline-exporting.js',
            '/highchart_dashboard/static/lib/js/export-data.js',
        ],
        cssLibs:[
            '/highchart_dashboard/static/lib/css/highcharts.css',
        ],
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
                if(self.recordData.chart_type == 'kpi'){
                    var $chart_container = self.$el.find('#chart_container');
                    $chart_container.html('');
                    var $kpiTemplate = QWeb.render('kpi_template', {
                        icon_option: self.recordData.icon_option,
                        upload_icon_binary: self.recordData.upload_icon_binary,
                        default_icon:self.recordData.default_icon,
                        icon_color: self.recordData.icon_color,
                        template_name: self.recordData.name ? self.recordData.name : self.recordData.model_id.name,
                        template_count: self.recordData.kpi_value,
                        second_model: self.recordData.second_model_id ? true : false,
                        data_comparision: self.recordData.data_comparision,
                        kpi_target: self.recordData.kpi_target,
                        target_display_value: self.recordData.target_display_value,
                        target_value_type: self.recordData.target_value_type,
                        kpi_target_view_type: self.recordData.kpi_target_view_type,
                    });
                    $chart_container.html($kpiTemplate);
                    $chart_container.css({"color":self.recordData.font_color, "background-color":self.recordData.background_color, "border-radius":"6px", "width":"300px","height":"unset"});
                    $chart_container.find('div.kpi_template_icon').css({"color":self.recordData.icon_color});
                    if (self.recordData.kpi_target && self.recordData.kpi_target_view_type == 'progress_bar'){
                        $chart_container.find('progress#target_progress_bar')[0].value = self.recordData.progress_bar_value;
                        $chart_container.find('progress#target_progress_bar')[0].max = self.recordData.progress_bar_max;
                    }
                } else if(self.recordData.chart_type == 'tile'){
                    var $chart_container = self.$el.find('#chart_container');
                    $chart_container.html('');
                    if(self.recordData.tile_template == 'template1') {
                        var $tileTemplate1 = QWeb.render('tile_template1', {
                            icon_option: self.recordData.icon_option,
                            upload_icon_binary: self.recordData.upload_icon_binary,
                            default_icon:self.recordData.default_icon + ' fa-5x',
                            icon_color: self.recordData.icon_color,
                            template_name: self.recordData.name ? self.recordData.name : self.recordData.model_id.name,
                            template_count: fieldUtils.format.integer(self.recordData.total_record),
                        });
                        $chart_container.html($tileTemplate1);
                        $chart_container.css({"color":self.recordData.font_color, "background-color":self.recordData.background_color, "border-radius":"6px", "width":"300px"});
                    } else if(self.recordData.tile_template == 'template2'){
                        var $tileTemplate2 = QWeb.render('tile_template2', {
                            icon_option: self.recordData.icon_option,
                            upload_icon_binary: self.recordData.upload_icon_binary,
                            default_icon:self.recordData.default_icon + ' fa-5x',
                            icon_color: self.recordData.icon_color,
                            template_name: self.recordData.name ? self.recordData.name : self.recordData.model_id.name,
                            template_count: fieldUtils.format.integer(self.recordData.total_record),
                        });
                        $chart_container.html($tileTemplate2);
                        $chart_container.css({"color":self.recordData.font_color, "background-color":self.recordData.background_color, "border-radius":"6px", "width":"300px"});
                    } else if(self.recordData.tile_template == 'template3'){
                        var $tileTemplate3 = QWeb.render('tile_template3', {
                            icon_option: self.recordData.icon_option,
                            upload_icon_binary: self.recordData.upload_icon_binary,
                            default_icon:self.recordData.default_icon + ' fa-5x',
                            icon_color: self.recordData.icon_color,
                            template_name: self.recordData.name ? self.recordData.name : self.recordData.model_id.name,
                            template_count: fieldUtils.format.integer(self.recordData.total_record),
                        });
                        $chart_container.html($tileTemplate3);
                        $chart_container.css({"color":self.recordData.font_color, "background-color":self.recordData.background_color, "border-radius":"6px", "width":"300px"});
                    } else if(self.recordData.tile_template == 'template4'){
                        var $tileTemplate4 = QWeb.render('tile_template4', {
                            icon_option: self.recordData.icon_option,
                            upload_icon_binary: self.recordData.upload_icon_binary,
                            default_icon:self.recordData.default_icon + ' fa-5x',
                            icon_color: self.recordData.icon_color,
                            template_name: self.recordData.name ? self.recordData.name : self.recordData.model_id.name,
                            template_count: fieldUtils.format.integer(self.recordData.total_record),
                        });
                        $chart_container.html($tileTemplate4);
                        $chart_container.css({"color":self.recordData.font_color, "background-color":self.recordData.background_color, "border-radius":"6px", "width":"300px"});
                    } else if(self.recordData.tile_template == 'template5'){
                        var $tileTemplate5 = QWeb.render('tile_template5', {
                            icon_option: self.recordData.icon_option,
                            upload_icon_binary: self.recordData.upload_icon_binary,
                            default_icon:self.recordData.default_icon + ' fa-5x',
                            icon_color: self.recordData.icon_color,
                            template_name: self.recordData.name ? self.recordData.name : self.recordData.model_id.name,
                            template_count: fieldUtils.format.integer(self.recordData.total_record),
                        });
                        $chart_container.html($tileTemplate5);
                        $chart_container.css({"color":self.recordData.font_color, "background-color":self.recordData.background_color, "border-radius":"6px", "width":"300px"});
                    } else if(self.recordData.tile_template == 'template6'){
                        var $tileTemplate6 = QWeb.render('tile_template6', {
                            icon_option: self.recordData.icon_option,
                            upload_icon_binary: self.recordData.upload_icon_binary,
                            default_icon:self.recordData.default_icon + ' fa-5x',
                            icon_color: self.recordData.icon_color,
                            template_name: self.recordData.name ? self.recordData.name : self.recordData.model_id.name,
                            template_count: fieldUtils.format.integer(self.recordData.total_record),
                        });
                        $chart_container.html($tileTemplate6);
                        $chart_container.css({"color":self.recordData.font_color, "background-color":self.recordData.background_color, "border-radius":"6px", "width":"300px"});
                    }
                } else if(self.recordData.chart_type == 'list_view'){
                    var $chart_container = self.$el.find('#chart_container');
                    self.$el.find('#chart_container').css({"width":"95%", "height": "350px", 'overflow': 'scroll'});
                    $chart_container.html('');
                    var $ListView = QWeb.render('ListViewPreview', {
                        chartData: JSON.parse(self.recordData.chart_data),
                    });
                    $chart_container.html($ListView);
                } else {
                    self.$el.find('#chart_container').html('');
                    self.$el.find('#chart_container').css({"width":"95%", "height": "350px"});
                    var options = JSON.parse(self.recordData.chart_data);
                    if (options.chart){
                        setTimeout(function(){ Highcharts.chart(options); }, 300);
                    }
                }
            });
        },


    });
    registry.add('dashboard_chart_preview', DashboardChartPreview);

    return {
        DashboardChartPreview: DashboardChartPreview,
    };

});