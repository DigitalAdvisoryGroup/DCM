odoo.define('highchart_dashboard.dashboard', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    var Widget = require('web.Widget');
    var _t = core._t;
    var session = require('web.session');
    var fieldUtils = require('web.field_utils');
    var AbstractAction = require('web.AbstractAction');


    var HighchartDashboard = AbstractAction.extend({

        jsLibs: [
            '/highchart_dashboard/static/lib/js/highcharts.js',
            '/highchart_dashboard/static/lib/js/highcharts-more.js',
            '/highchart_dashboard/static/lib/js/exporting.js',
            '/highchart_dashboard/static/lib/js/offline-exporting.js',
            '/highchart_dashboard/static/lib/js/export-data.js',
            '/highchart_dashboard/static/lib/js/gridstack.min.js',
            '/highchart_dashboard/static/lib/js/gridstack.jQueryUI.min.js',
        ],

        cssLibs: [
            '/highchart_dashboard/static/lib/css/gridstack.min.css',
            '/highchart_dashboard/static/lib/css/highcharts.css',
        ],

        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.controllerID = params.controllerID;
            this.action_manager = parent;
            this.currentDashboardData = [];
            this.dashboardDateFilter = 'None';
            this.client_action_id = state.id;
            this.dashboard_id = false;
            this.sizeAndMoveChanges = {};
            this.filterName = {
                'none': 'None',
                'today': 'Today',
                'last_day': 'Last Day',
                'last_week': 'Last Week',
                'last_month': 'Last Month',
                'last_quarter': 'Last Quarter',
                'last_year': 'Last Year',
                'this_week': 'This Week',
                'this_month': 'This Month',
                'this_quarter': 'This Quarter',
                'this_year': 'This Year',
                'next_day': 'Next Day',
                'next_week': 'Next Week',
                'next_month': 'Next Month',
                'next_quarter': 'Next Quarter',
                'next_year': 'Next Year',
                'last_7_days': 'Last 7 Days',
                'last_30_days': 'Last 30 Days',
                'last_90_days': 'Last 90 Days',
                'last_365_days': 'Last 365 Days',
                'custom': 'Custom',
                'None': 'none',
                'Today': 'today',
                'Last Day': 'last_day',
                'Last Week': 'last_week',
                'Last Month': 'last_month',
                'Last Quarter': 'last_quarter',
                'Last Year': 'last_year',
                'This Week': 'this_week',
                'This Month': 'this_month',
                'This Quarter': 'this_quarter',
                'This Year': 'this_year',
                'Next Day': 'next_day',
                'Next Week': 'next_week',
                'Next Month': 'next_month',
                'Next Quarter': 'next_quarter',
                'Next Year': 'next_year',
                'Last 7 Days': 'last_7_days',
                'Last 30 Days': 'last_30_days',
                'Last 90 Days': 'last_90_days',
                'Last 365 Days': 'last_365_days',
                'Custom': 'custom'
            };
        },

        events: {
            // Chart Options
            'click .dashboard_chart_info': 'dashboardChartInfo',
            'click .all_dashboard_dropdown_ul': 'dashboardDropdownUlClick',
            'click .dashboard_chart_duplicate': 'dashboardChartDuplicate',
            'click .dashboard_chart_move': 'dashboardChartMove',
            'click .dashboard_edit_chart': 'dashboardEditChart',
            'click .dashboard_remove_chart': 'dashboardRemoveChart',

            // Dashboard Date Filter
            'click .dashboard_date_filter>li': '_onDateFilterClick',
            'click .dashboard_apply_date_filter': '_onApplyDateFilterClick',
            'click .dashboard_clear_date_filter': '_onClearDateFilterClick',

            // Dashboard Edit and Add Chart
            'click .add_chart_selection>li': '_onAddChartTypeClick',
            'click #highchart_edit_layout': 'highchartEditLayout',
            'click .dashboard_save_layout': 'highchartEditSaveLayout',
            'click .dashboard_cancel_layout': 'highchartEditCancelLayout',

            // Drag and Drop Chart
            'dragstop .grid-stack': 'dragStopEvent',
            'gsresizestop .grid-stack': 'gsResizeStop',
        },

        dashboardDropdownUlClick: function (event) {
            event.stopPropagation();
        },

        dashboardChartInfo: function (event) {
            var self = this;
            var $event = $(event.currentTarget);
            var chartId = $event.attr('data-chart-id');
            var chartData = {};
            _.each(self.currentDashboardData, function (chart) {
                if (chart.chart_id == chartId) {
                    chartData = chart;
                }
            });
            if(chartData.domain && chartData.domain.includes("%UID")){
                chartData.domain = chartData.domain.replace('"%UID"', session.user_context.uid)
            }
            clearInterval(self.myInterval);
            var action = {
                name: _t(chartData.name),
                type: 'ir.actions.act_window',
                res_model: chartData.model_name,
                domain: chartData.domain,
                context: {'group_by': chartData.group_by},
                views: [
                    [chartData.list_view_ref ? chartData.list_view_ref : false, 'list'],
                    [chartData.form_view_ref ? chartData.form_view_ref : false, 'form']
                ],
                view_mode: 'list',
                target: 'current',
            }
            self.do_action(action);
        },

        dashboardChartDuplicate: function (event) {
            var self = this;
            var $event = $(event.currentTarget);
            var chartId = $event.attr('data-chart-id');
            var $dashboardSelector = self.$el.find('#dashboard_dropdown_selector_' + chartId);
            var dashboardId = $dashboardSelector.children("option:selected").val()
            this._rpc({
                model: 'highchart.dashboard.chart',
                method: 'duplicate_dashboard_chart',
                args: [[parseInt(chartId)], dashboardId],
            }).then(function () {
                var dashboardData = self.get_dashboard_data();
                Promise.all([dashboardData]).then(function () {
                    self.$el.html('');
                    self.renderHighchartDashboard();
                });
            });
        },

        dashboardChartMove: function (event) {
            var self = this;
            var $event = $(event.currentTarget);
            var chartId = $event.attr('data-chart-id');
            var $dashboardSelector = self.$el.find('#dashboard_dropdown_selector_' + chartId);
            var dashboardId = $dashboardSelector.children("option:selected").val()
            this._rpc({
                model: 'highchart.dashboard.chart',
                method: 'move_dashboard_chart',
                args: [[parseInt(chartId)], dashboardId],
            }).then(function () {
                var dashboardData = self.get_dashboard_data();
                Promise.all([dashboardData]).then(function () {
                    self.$el.html('');
                    self.renderHighchartDashboard();
                });
            });
        },

        dashboardEditChart: function (event) {
            var self = this;
            var $event = $(event.currentTarget);
            var chartId = parseInt($event.attr('data-chart-id'));
            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'highchart.dashboard.chart',
                view_id: 'view_highchart_dashboard_chart_form',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                res_id: chartId,
            },{
                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
            });
        },

        dashboardRemoveChart: function (event) {
            var self = this;
            var $event = $(event.currentTarget);
            var chartId = $event.attr('data-chart-id');

            this._rpc({
                model: 'highchart.dashboard.chart',
                method: 'unlink',
                args: [[parseInt(chartId)]],
            }).then(function () {
                var dashboardData = self.get_dashboard_data();
                Promise.all([dashboardData]).then(function () {
                    self.$el.html('');
                    self.renderHighchartDashboard();
                });
            });
        },



        _onClearDateFilterClick: function (ev) {
            var self = this;
            self.dashboardDateFilter = 'None';
            var getData = self.get_dashboard_data();
            Promise.resolve(getData).then(function () {
                $(self.$el[0]).html('');
                self.renderHighchartDashboard();
            });
        },

        _onAddChartTypeClick: function (ev) {
            var self = this;
            var context = {};
            context['default_dashboard_id'] = self.dashboard_id;
            context['default_chart_type'] = ev.currentTarget.dataset.type;
            self.do_action({
                name: _t(self.dashboardName),
                type: 'ir.actions.act_window',
                res_model: 'highchart.dashboard.chart',
                view_id: 'view_highchart_dashboard_chart_form',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: context,
            },{
                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
            });
        },
        on_reverse_breadcrumb: function(state) {
            this.start();
        },

        willStart: function () {
            var self = this;
            var dashboardFilterType = 'none';
            return $.when(ajax.loadLibs(this), this._super());
        },

        _onApplyDateFilterClick: function (ev) {
            var self = this;
            var dashboardId = self.dashboard_id;
            var dateFilter = 'custom';
            var $filterStartDate = self.$el.find('#custom_start_date');
            var $filterEndDate = self.$el.find('#custom_end_date');
            var getData = self.get_dashboard_data(dateFilter, $filterStartDate[0].value, $filterEndDate[0].value);
            Promise.resolve(getData).then(function () {
                $(self.$el[0]).html('');
                self.renderHighchartDashboard();
            });
        },

        _onDateFilterClick: function (ev) {
            var self = this;
            var dashboardId = self.dashboard_id;
            var dateFilter = ev.currentTarget.dataset.type;
            self.dashboardDateFilter = self.filterName[dateFilter];
            if (dateFilter === 'custom') {
                $('.dashboard_date_filter_inputs').css({'display': 'inline-block'});
                if ($(ev.target).data('type') == 'custom') {
                    $(ev.target).parents().find('#highchart_date_filter_name').html('Custom')
                }
            } else if (dateFilter !== 'custom') {
                var getData = self.get_dashboard_data(dateFilter);
                Promise.resolve(getData).then(function () {
                    $(self.$el[0]).html('');
                    self.renderHighchartDashboard();
                });
            }
        },

        get_dashboard_data: function (dashboardFilterType, filter_start_date, filter_end_date) {
            var self = this;
            return this._rpc({
                model: 'highchart.dashboard',
                method: 'get_dashboard_data',
                args: [self.client_action_id, dashboardFilterType, filter_start_date, filter_end_date],
            }).then(function (values) {
                values = JSON.parse(values);
                self.dashboard_id = values['dashboard_id'];
                self.refreshInterval = parseInt(values['refresh_interval']);
                self.dashboardName = values['dashboard_name'];
                self.allDashboards = values['all_dashboards'];
                self.currentDashboardData = values['dashboard_charts'];
            });
        },

        start: function () {
            var self = this;
            self.get_dashboard_data().then(function () {
                if (self.refreshInterval > 0) {
                    self.updateDashboardOnInterval();
                }
                self.renderHighchartDashboard();
            });
            return this._super.apply(this, arguments);
        },

        updateDashboardOnInterval: function () {
            var self = this;
            self.myInterval = setInterval(function () {
                var getData = self.get_dashboard_data();
                Promise.resolve(getData).then(function () {
                    $(self.$el[0]).html('');
                    self.renderHighchartDashboard();
                });
            }, self.refreshInterval);
        },

        renderHighchartDashboard: function () {
            var self = this;
            var $dashboard = $(QWeb.render('highchartMainDashboard', {
                dashboardId: self.dashboard_id,
                dashboardName: self.dashboardName,
                dashboardDateFilter: self.dashboardDateFilter,
                allDashboards: self.allDashboards,
                chartData: self.currentDashboardData,
            }));
            if(self.$el.find('.o_content').length){
                self.$el.find('.o_content').hide();
            }
            self.$el.html($dashboard)
            self.$el.attr('style','overflow: scroll;')
            if (self.dashboardDateFilter == 'Custom'){
                $('.dashboard_date_filter_inputs').css({'display': 'inline-block'});
            }

            self.$el.find('#custom_start_date').datepicker({
                onSelect: function (custom_start_date) {
                    var $filterStartDate = self.$el.find('#custom_start_date');
                    var $filterEndDate = self.$el.find('#custom_end_date');
                    if ($filterStartDate[0].value.length != 0 && $filterEndDate[0].value.length != 0) {
                        self.$el.find('.dashboard_date_filter_buttons').removeClass('hide_element');
                        self.$el.find('.dashboard_date_filter_buttons').css({'display': 'inline-block'});
                    } else {
                        self.$el.find('.dashboard_date_filter_buttons').addClass('hide_element');
                    }

                    self.$el.find(".dashboard_apply_date_filter").removeClass("hide_element");
                    self.$el.find(".dashboard_clear_date_filter").removeClass("hide_element");
                },
            });
            self.$el.find('#custom_end_date').datepicker({
                onSelect: function (custom_end_date) {
                    var $filterStartDate = self.$el.find('#custom_start_date');
                    var $filterEndDate = self.$el.find('#custom_end_date');
                    if ($filterStartDate[0].value.length != 0 && $filterEndDate[0].value.length != 0) {
                        self.$el.find('.dashboard_date_filter_buttons').removeClass('hide_element');
                        self.$el.find('.dashboard_date_filter_buttons').css({'display': 'inline-block'});
                    } else {
                        self.$el.find('.dashboard_date_filter_buttons').addClass('hide_element');
                    }

                    self.$el.find(".dashboard_apply_date_filter").removeClass("hide_element");
                    self.$el.find(".dashboard_clear_date_filter").removeClass("hide_element");
                },
            });

            self.$el.find('.grid-stack').gridstack();
            self.$el.find('.grid-stack').data('gridstack').disable();

            Promise.all([$dashboard]).then(function () {
                _.each(self.currentDashboardData, function (chartData) {
                    var $chart_container = self.$el.find('#chart_container_' + chartData['chart_id']);
                    if (chartData.chart_type == 'list_view') {
                        var $ListView = QWeb.render('ListViewPreview', {
                            chartData: JSON.parse(chartData.chart_data),
                        });
                        $chart_container.html($ListView);
                        $chart_container.find('div#list_view_table').css({'padding-top': '40px'})
                    } else if (chartData.chart_type == 'kpi') {
                        var $kpiTemplate = QWeb.render('kpi_template', {
                            icon_option: chartData.icon_option,
                            upload_icon_binary: chartData.upload_icon_binary,
                            default_icon: chartData.default_icon,
                            icon_color: chartData.icon_color,
                            template_name: chartData.name ? chartData.name : chartData.model_id.name,
                            template_count: chartData.kpi_value,
                            second_model: chartData.second_model_id ? true : false,
                            kpi_target: chartData.kpi_target,
                            target_display_value: chartData.target_display_value,
                            data_comparision: chartData.data_comparision,
                            target_value_type: chartData.target_value_type,
                            kpi_target_view_type: chartData.kpi_target_view_type,
                        });
                        $chart_container.html($kpiTemplate);
                        $chart_container.css({
                            "color": chartData.font_color,
                            "background-color": chartData.background_color,
                            "border-radius": "6px"
                        });

                        $chart_container.find('div.kpi_template_icon').css({"color": chartData.icon_color});
                        if (chartData.kpi_target && chartData.kpi_target_view_type == 'progress_bar') {
                            $chart_container.find('progress#target_progress_bar')[0].value = chartData.progress_bar_value;
                            $chart_container.find('progress#target_progress_bar')[0].max = chartData.progress_bar_max;
                        }
                    } else if (chartData.chart_type == 'tile') {
                        if (chartData.tile_template == 'template1') {
                            var $tileTemplate1 = QWeb.render('tile_template1', {
                                icon_option: chartData.icon_option,
                                upload_icon_binary: chartData.upload_icon_binary,
                                default_icon: chartData.default_icon + ' fa-5x',
                                icon_color: chartData.icon_color,
                                template_name: chartData.name ? chartData.name : chartData.model_id.name,
                                template_count: fieldUtils.format.integer(chartData.total_record),
                            });
                            $chart_container.html($tileTemplate1);
                            $chart_container.css({
                                "color": chartData.font_color,
                                "background-color": chartData.background_color,
                                "border-radius": '6px'
                            });
                        } else if (chartData.tile_template == 'template2') {
                            var $tileTemplate2 = QWeb.render('tile_template2', {
                                icon_option: chartData.icon_option,
                                upload_icon_binary: chartData.upload_icon_binary,
                                default_icon: chartData.default_icon + ' fa-5x',
                                icon_color: chartData.icon_color,
                                template_name: chartData.name ? chartData.name : chartData.model_id.name,
                                template_count: fieldUtils.format.integer(chartData.total_record),
                            });
                            $chart_container.html($tileTemplate2);
                            $chart_container.css({
                                "color": chartData.font_color,
                                "background-color": chartData.background_color,
                                "border-radius": '6px'
                            });
                        } else if (chartData.tile_template == 'template3') {
                            var $tileTemplate3 = QWeb.render('tile_template3', {
                                icon_option: chartData.icon_option,
                                upload_icon_binary: chartData.upload_icon_binary,
                                default_icon: chartData.default_icon + ' fa-5x',
                                icon_color: chartData.icon_color,
                                template_name: chartData.name ? chartData.name : chartData.model_id.name,
                                template_count: fieldUtils.format.integer(chartData.total_record),
                            });
                            $chart_container.html($tileTemplate3);
                            $chart_container.css({
                                "color": chartData.font_color,
                                "background-color": chartData.background_color,
                                "border-radius": '6px'
                            });
                        } else if (chartData.tile_template == 'template4') {
                            var $tileTemplate4 = QWeb.render('tile_template4', {
                                icon_option: chartData.icon_option,
                                upload_icon_binary: chartData.upload_icon_binary,
                                default_icon: chartData.default_icon + ' fa-5x',
                                icon_color: chartData.icon_color,
                                template_name: chartData.name ? chartData.name : chartData.model_id.name,
                                template_count: fieldUtils.format.integer(chartData.total_record),
                            });
                            $chart_container.html($tileTemplate4);
                            $chart_container.css({
                                "color": chartData.font_color,
                                "background-color": chartData.background_color,
                                "border-radius": '6px'
                            });
                        } else if (chartData.tile_template == 'template5') {
                            var $tileTemplate5 = QWeb.render('tile_template5', {
                                icon_option: chartData.icon_option,
                                upload_icon_binary: chartData.upload_icon_binary,
                                default_icon: chartData.default_icon + ' fa-5x',
                                icon_color: chartData.icon_color,
                                template_name: chartData.name ? chartData.name : chartData.model_id.name,
                                template_count: fieldUtils.format.integer(chartData.total_record),
                            });
                            $chart_container.html($tileTemplate5);
                            $chart_container.css({
                                "color": chartData.font_color,
                                "background-color": chartData.background_color,
                                "border-radius": '6px'
                            });
                        } else if (chartData.tile_template == 'template6') {
                            var $tileTemplate6 = QWeb.render('tile_template6', {
                                icon_option: chartData.icon_option,
                                upload_icon_binary: chartData.upload_icon_binary,
                                default_icon: chartData.default_icon + ' fa-5x',
                                icon_color: chartData.icon_color,
                                template_name: chartData.name ? chartData.name : chartData.model_id.name,
                                template_count: fieldUtils.format.integer(chartData.total_record),
                            });
                            $chart_container.html($tileTemplate6);
                            $chart_container.css({
                                "color": chartData.font_color,
                                "background-color": chartData.background_color,
                                "border-radius": '6px'
                            });
                        }
                    } else if (chartData.chart_type != 'tile' || chartData.chart_type != 'kpi' || chartData.chart_type != 'list_view') {
                        var options = JSON.parse(chartData.chart_data);
                        delete options['chart']['renderTo'];
                        Highcharts.chart($chart_container[0], options);
                    }
                });
            });
        },

        highchartEditLayout: function (ev) {
            var self = this;
            $('.highchart_date_filter_button_div').hide();
            $('.highchart_add_chart_button_div').hide();
            $('a#highchart_edit_layout').hide();
            $('button#highchart_edit_layout').attr('style','display:none !important;');
            $('#highchart_edit_layout').hide();
            $('.dashboard_edit_mode_buttons').show();
            self.$el.find('.grid-stack').data('gridstack').enable();
        },

        highchartEditSaveLayout: function (ev) {
            var self = this;
            $('.highchart_date_filter_button_div').show();
            $('.highchart_add_chart_button_div').show();
            $('a#highchart_edit_layout').show();
            $('button#highchart_edit_layout').show();
            $('button#highchart_edit_layout').removeAttr()
            $('.dashboard_edit_mode_buttons').hide();
            self.$el.find('.grid-stack').data('gridstack').disable();
            self.write_dashboard_data();
            self.sizeAndMoveChanges = {};
            self.willStart();
        },

        write_dashboard_data: function () {
            var self = this;
            return this._rpc({
                model: 'highchart.dashboard',
                method: 'write_dashboard_data',
                args: [self.dashboard_id, self.sizeAndMoveChanges],
            }).then(function () {
                self.get_dashboard_data();
            });
        },

        highchartEditCancelLayout: function (ev) {
            var self = this;
            self.$el.html('');
            self.sizeAndMoveChanges = {};
            self.renderHighchartDashboard();
        },

        dragStopEvent: function (event, ui) {
            var self = this;
            var element = event.target;
            var $new_element = element

            setTimeout(function () {
                var gridStackItem = self.$el.find('.grid-stack').find("div[class*='grid-stack-item item-unset-relative']")
                _.each(gridStackItem, function (stackItem) {
                    var chartId = $(stackItem).attr('data-gs-id');
                    var newX = $(stackItem).attr('data-gs-x');
                    var newY = $(stackItem).attr('data-gs-y');
                    var newHeight = $(stackItem).attr('data-gs-height');
                    var newWidth = $(stackItem).attr('data-gs-width');
                    self.sizeAndMoveChanges[chartId] = {
                        'gs_x': newX,
                        'gs_y': newY,
                        'gs_height': newHeight,
                        'gs_width': newWidth
                    }
                });
            }, 300);
        },

        gsResizeStop: function (event, elem) {
            var self = this;
            var newHeight = $(elem).attr('data-gs-height');
            var newWidth = $(elem).attr('data-gs-width');
            var $chart_container = $(elem).find('.graph_container');
            var chartId = $chart_container.attr('data-chart-id');
            _.each(self.currentDashboardData, function (chartData) {
                if (chartData.chart_type != 'tile' && chartData.chart_type != 'kpi' && chartData.chart_type != 'list_view' && chartData.chart_id == chartId) {
                    var options = JSON.parse(chartData.chart_data);
                    delete options['chart']['renderTo'];
                    Highcharts.chart($chart_container[0], options);
                }
            });

            var gridStackItem = self.$el.find('.grid-stack').find("div[class*='grid-stack-item item-unset-relative']")
            _.each(gridStackItem, function (stackItem) {
                var chartId = $(stackItem).attr('data-gs-id');
                var newX = $(stackItem).attr('data-gs-x');
                var newY = $(stackItem).attr('data-gs-y');
                var newHeight = $(stackItem).attr('data-gs-height');
                var newWidth = $(stackItem).attr('data-gs-width');
                self.sizeAndMoveChanges[chartId] = {
                    'gs_x': newX,
                    'gs_y': newY,
                    'gs_height': newHeight,
                    'gs_width': newWidth
                }
            });
        },

    });
    core.action_registry.add('highchart_main_dashboard', HighchartDashboard);

    return HighchartDashboard

});
