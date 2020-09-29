odoo.define('many2many_tags_click.many2many', function (require) {
    "use strict";

    var relational_fields = require('web.relational_fields');
    var FieldMany2ManyTags = relational_fields.FieldMany2ManyTags;
    var registry = require('web.field_registry');

    var FieldMany2manyOpen = FieldMany2ManyTags.extend({
        _renderTags: function () {
            this._super.apply(this, arguments)
            if(this.mode == 'readonly'){
                this.$el.on('click', 'div.badge-pill', this.onOpenRecordTag.bind(this));
            }
        },
        onOpenRecordTag:function(ev){
            var data = $(ev.target).parent().data();
            if(data && data.id != undefined && data.id){
                this.do_action({
                    res_id: data.id,
                    res_model: this.field.relation,
                    type: 'ir.actions.act_window',
                    views: [[false, 'form']],
                });
            }
        },
        _getRenderTagsContext: function () {
            var result = this._super.apply(this, arguments);
            result.res_model = this.field.relation;
            return result;
        },
    });
    registry
    .add('many2many_tags_open', FieldMany2manyOpen)
    return FieldMany2manyOpen

    
});

