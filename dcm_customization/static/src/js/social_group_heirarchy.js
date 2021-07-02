odoo.define('dcm_customization.social_group_heirarchy', function(require) {
    'use strict';
    var ajax = require('web.ajax');
    $(document).ready(function() {
        if ($('.social_group_hierarchy').length > 0) {
            ajax.jsonRpc('/get_tree_heirarchy_details', 'call', {
                'search': $('input[name="social_group_search"]').val(),
                'social_group_id': $('input[name="social_group_id"]').val(),
                'token': $('input[name="token"]').val()
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
               // 'token': $('input[name="token"]').val()
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
                'social_group_id': $('#sunburst-container').attr('group-id'),
                'token': $('#sunburst-container').attr('token'),
            }).then(function(result) {
                // Splice in transparent for the center circle
                Highcharts.getOptions().colors.splice(0, 0, 'transparent');
                console.log("----asdasd--------------",Highcharts.getOptions().colors)
                Highcharts.chart('sunburst-container', {
                plotOptions: {
                     sunburst: {
                        allowTraversingTree:true,
                    }
                },
                    chart: {
                        height: '100%'
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
                                if (event.point.innerArcLength === 0) {
                                    $('#group_name > a').attr({'href': '/midardir/socialgroup/'+ event.point.parent_id +'?token='+ event.point.token +'&search=&parent='});
                                    $('#group_name > a').text(event.point.parent_name);
                                    $('#leadership_name > a').attr({'href': '/midardir/contact/'+ event.point.parent_group_owner_id +'?token='+ event.point.token +'&search=&parent='});
                                    $('#leadership_name > a').text(event.point.parent_group_owner_name);
                                    $('#headcount_direct').text('Headcount Direct: ' + event.point.parent_current_subscribers_count);
                                    $('#headcount_total').text('Headcount Total: ' + event.point.parent_value);
                                    $('#headcount_bit').text('BIT: ' + event.point.parent_current_ext_subscribers_count);
                                    $('#headcount_external').text('External: ' + event.point.parent_current_and_childs_ext_subscribers_count);
                                    if(typeof event.point.drillId === "undefined") {
                                        window.location.href = '/midardir/socialgroup/'+ event.point.parent_id +'?token='+ event.point.token +'&search=&parent='
                                    }
                                } else {
                                    $('#group_name > a').attr({'href': '/midardir/socialgroup/'+ event.point.id +'?token='+ event.point.token +'&search=&parent='});
                                    $('#group_name > a').text(event.point.name);
                                    $('#leadership_name > a').attr({'href': '/midardir/contact/'+ event.point.group_owner_id +'?token='+ event.point.token +'&search=&parent='});
                                    $('#leadership_name > a').text(event.point.group_owner_name);
                                    $('#headcount_direct').text('Headcount Direct: ' + event.point.current_subscribers_count);
                                    $('#headcount_total').text('Headcount Total: ' + event.point.value);
                                    $('#headcount_bit').text('BIT: ' + event.point.current_ext_subscribers_count);
                                    $('#headcount_external').text('External: ' + event.point.current_and_childs_ext_subscribers_count);
                                    if(typeof event.point.drillId === "undefined") {
                                        window.location.href = '/midardir/socialgroup/'+ event.point.id +'?token='+ event.point.token +'&search=&parent='
                                    }
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
                                style: {'color': 'black'},
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