odoo.define('dcm_customization.social_group_heirarchy', function(require) {
    'use strict';
    var ajax = require('web.ajax');
    $(document).ready(function() {
        if ($('.social_group_hierarchy').length > 0) {
            ajax.jsonRpc('/get_tree_heirarchy_details', 'call', {
                'search': $('input[name="social_group_search"]').val(),
                'social_group_id': $('input[name="social_group_id"]').val()
            }).then(function(result) {
                var count = 0
                _.each(result, function(value, key) {
                    console.log("Key==", key, value)
                    var temp_div = '<div id="tree_' + count.toString() + '"></div><br/>';
                    $('.social_group_hierarchy').append(temp_div)
                    $('#tree_' + count.toString()).tree({
                        data: [value],
                        autoOpen: false,
                        selectable: false,
                        autoEscape: false,
                        onCreateLi: function(node, $li) {
                            $li.find('.jqtree-toggler').attr('aria-hidden', false);
                        },
                    })
                    count += 1
                })
            })
        }
        if ($('#chart-container').length > 0) {
            ajax.jsonRpc('/get_heirarchy_details', 'call', {
                'social_group_id': $('#chart-container').attr('group-id')
            }).then(function(result) {
                console.log("Result---", result)
                var oc = $('#chart-container').orgchart({
                    'data': result,
                    'depth': 999,
                    'visibleLevel': 2,
                    'nodeContent': 'title',
                    'exportButton': false,
                    'exportFilename': 'OrgChart',
                    'exportFileextension': 'png',
                    'parentNodeSymbol': 'fa-users',
                    'draggable': true,
                    'direction': 't2b',
                    'pan': true,
                    'zoom': true,
                    'zoominLimit': 7,
                    'zoomoutLimit': 0.5
                });
                var $chart = $('.orgchart');
                oc.setChartScale($chart, 0.75);
            })
        }
        if ($('#sunburst-container').length > 0) {
            ajax.jsonRpc('/get_sunburst_details', 'call', {
                'social_group_id': $('#sunburst-container').attr('group-id')
            }).then(function(result) {
                // Splice in transparent for the center circle
                Highcharts.getOptions().colors.splice(0, 0, 'transparent');
                Highcharts.chart('sunburst-container', {
                plotOptions: {
                     sunburst: {
                        allowTraversingTree:true,
                    }
                },
                    chart: {
                        height: '70%'
                    },
                    title: {
                        text: ''
                    },
//                    subtitle: {
//                        text: result.upper_level
//                    },
                    series: [{
                        events: {
                            click: function (event) {
                                console.log('------------ event ------------', event)
                                $('#group_name').text(event.point.name);
                                $('#leadership_name').text('Leadership: ' + event.point.group_owner_name);
                                $('#headcount_direct').text('Headcount Direct: ' + event.point.current_subscribers_count);
                                $('#headcount_total').text('Headcount Total: ' + event.point.value);
                                if(typeof event.point.drillId === "undefined") {
                                    window.location.href = '/midardir/socialgroup/' + event.point.id
                                }
                            }
                        },
                        type: 'sunburst',
                        panning : true,
                        pinchType: 'none',
                        resetZoomButton: {
                            theme: {
                                display: 'none'
                            }
                        },
                        data: result.data,
                        allowDrillToNode: true,
                        cursor: 'pointer',
                        dataLabels: {
                            style: {
                                textOutline: "0px",
                            },
                            format: '{point.name}',
                            filter: {
                                property: 'innerArcLength',
                                operator: '>',
                                value: 16
                            },
                            rotationMode: 'circular'
                        },
                        levels: [{
                            level: 1,
                            levelIsConstant: false,

                            dataLabels: {
                                style: {'font-color': 'black'},
                                filter: {
                                    property: 'outerArcLength',
                                    operator: '>',
                                    value: 64
                                }
                            }
                        }, {
                            level: 2,
                            colorByPoint: true
                        },
//                        {
//                            level: 3,
////                            colorByPoint: true,
//                            colorVariation: {
//                                key: 'brightness',
//                                to: -0.5
//                            }
//                        }, {
//                            level: 4,
//                            colorVariation: {
//                                key: 'brightness',
//                                to: 0.5
//                            }
//                        }
                        ]
                    }],
                    tooltip: {
                        headerFormat: '',
                        pointFormat: 'The head count of <b>{point.name}</b> is <b>{point.value}</b>'
                    }
                });

            })
        }
    });
});