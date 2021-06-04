odoo.define('dcm_customization.social_group_heirarchy', function (require) {
    'use strict';
    
    var ajax = require('web.ajax');
    
    $(document).ready(function(){
    	if($('#chart-container').length > 0) {
    		ajax.jsonRpc('/get_heirarchy_details','call',{'social_group_id' : $('#chart-container').attr('group-id')}).then(function(result){
    			console.log("Result---",result)
//    			var org_chart = $('#chart-container').orgChart({
//				    data: result,// your data
//				    showControls:true,// display add or remove node button.
//				    allowEdit:true,// click the node's title to edit
//				    onAddNode:function(node){},
//			        onDeleteNode:function(node){},
//			        onClickNode:function(node){},
//			        newNodeText: 'Add Child'// text of add button
//
//				});

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
    			
//    			$("#chart-container").jHTree({
//    				  callType:'obj',
//    				  structureObj: [result],
//    				  zoomer:true
//				});
//    			var count = 0
//    			_.each(result,function(value,key){
//    				console.log("Key==",key,value)
//
//    				var temp_div = '<strong>' + key + '</strong><div id="tree_' + count.toString() + '"></div><br/>';
//
//    				$('.social_group_hierarchy').append(temp_div)
//    				$('#tree_' + count.toString()).tree({
//    					data: value,
//    					autoOpen: true,
//    					selectable: false,
//    					autoEscape : false,
//    					onCreateLi: function(node, $li) {
//    						$li.find('.jqtree-toggler').attr('aria-hidden',false);
//    					},
//    				})
//    				count += 1
//    			})
    		})
    	}
    })
    
    
});