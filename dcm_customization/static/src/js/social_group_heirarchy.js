odoo.define('dcm_customization.social_group_heirarchy', function (require) {
    'use strict';
    
    var ajax = require('web.ajax');
    
    $(document).ready(function(){
    	if($('.social_group_hierarchy').length > 0) {
    		ajax.jsonRpc('/get_tree_heirarchy_details','call',{'search' : $('input[name="social_group_search"]').val(),'social_group_id' : $('input[name="social_group_id"]').val()}).then(function(result){
    			var count = 0
    			_.each(result,function(value,key){
    				console.log("Key==",key,value)
    				
    				var temp_div = '<div id="tree_' + count.toString() + '"></div><br/>';
    				
    				$('.social_group_hierarchy').append(temp_div)
    				
    				$('#tree_' + count.toString()).tree({
    					data: [value],
    					autoOpen: false,
    					selectable: false,
    					autoEscape : false,
    					onCreateLi: function(node, $li) {
    						$li.find('.jqtree-toggler').attr('aria-hidden',false);
    					},
    				})
    				count += 1
    			})
    		})
    	}
    	if($('#chart-container').length > 0) {
    		ajax.jsonRpc('/get_heirarchy_details','call',{'social_group_id' : $('#chart-container').attr('group-id')}).then(function(result){
    			console.log("Result---",result)
    			var oc = $('#chart-container').orgchart({
    			      'data' : result,
    			      'depth': 999,
    			      'visibleLevel': 2,
    			      'nodeContent': 'title',
    			      'exportButton':false,
    			      'exportFilename':'OrgChart',
    			      'exportFileextension':'png',
    			      'parentNodeSymbol':'fa-users',
    			      'draggable':true,
    			      'direction':'t2b',
    			      'pan':true,
    			      'zoom':true,
    			      'zoominLimit': 7,
    			      'zoomoutLimit': 0.5
			    });
    			
    			var $chart = $('.orgchart');
    			oc.setChartScale($chart, 0.75);
    		})
    	}
    	if ($('#sunburst-container').length > 0){
    	    ajax.jsonRpc('/get_sunburst_details','call',{'social_group_id' : $('#sunburst-container').attr('group-id')}).then(function(result){
    	    console.log("-------result.data----------",result.data)
    	        Highcharts.chart('sunburst-container', {

                    chart: {
                        height: '70%'
                    },

                    // Let the center circle be transparent
//                    colors: ['transparent'].concat(Highcharts.getOptions().colors),
                    colors: ['transparent',"#7cb5ec", "#90ed7d","#434348", "#f7a35c", "#8085e9", "#f15c80", "#e4d354", "#2b908f", "#f45b5b", "#91e8e1"],

                    title: {
                        text: result.header
                    },

                    subtitle: {
                        text: 'Source <a href="https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)">Wikipedia</a>'
                    },

                    series: [{
                        type: 'sunburst',
                        data: result.data,
                        allowDrillToNode: true,
                        cursor: 'pointer',
                        dataLabels: {
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
                                filter: {
                                    property: 'outerArcLength',
                                    operator: '>',
                                    value: 64
                                }
                            }
                        },
                        {
                            level: 2,
                            colorByPoint: true
                        }
                        ]

                    }],

                    tooltip: {
                        headerFormat: '',
                        pointFormat: 'The population of <b>{point.name}</b> is <b>{point.value}</b>'
                    }
                });
    	    });
        }
});
});