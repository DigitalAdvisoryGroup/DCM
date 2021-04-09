odoo.define('goGP.portal', function (require) {
    'use strict';
    $(document).ready(function(){
        $("div.show-more").on('click', function (ev) {
           if($(ev.currentTarget).parent().find('.d-none').length < 5){
             ev.currentTarget.hidden = true
           }
           $(ev.currentTarget).parent().find('.d-none').slice(0,5).removeClass("d-none");
        });
    });
});
