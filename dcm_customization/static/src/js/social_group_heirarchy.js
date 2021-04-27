odoo.define('dcm_customization.social_group_heirarchy', function (require) {
    'use strict';
    
    var ajax = require('web.ajax');
    
    $(document).ready(function(){
    	if($('.social_group_hierarchy').length > 0) {
    		ajax.jsonRpc('/get_heirarchy_details','call',{'search_query' : $('.search-query').val()}).then(function(result){
    			var count = 0
    			_.each(result,function(value,key){
    				console.log("Key==",key,value)
    				
    				var temp_div = '<strong>' + key + '</strong><div id="tree_' + count.toString() + '"></div><br/>';
    				
    				$('.social_group_hierarchy').append(temp_div)
    				$('#tree_' + count.toString()).tree({
    					data: value,
    					autoOpen: true,
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
    })
    
    
});