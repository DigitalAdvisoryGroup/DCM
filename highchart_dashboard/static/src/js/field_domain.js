odoo.define('highchart_dashboard.field_domain', function (require) {

    "use strict";

    var view_dialogs = require('web.view_dialogs');
    var BasicFields = require('web.basic_fields');
    var BasicModel = require('web.BasicModel');
    var core = require("web.core");

    var _t = core._t;
    BasicModel.include({
        _fetchSpecialDomain: function (e, a, t) {
            var c = a;
            return e._changes && e._changes[a] ? e._changes[a].includes("%UID") && (c = a + "_temp", e._changes[c] = e._changes[a].replace('"%UID"', e.getContext().uid)) : e.data[a] && e.data[a].includes("%UID") && (c = a + "_temp", e.data[c] = e.data[a].replace('"%UID"', e.getContext().uid)), this._super(e, c, t)
        }
    });

    BasicFields.FieldDomain.include({
        _onShowSelectionButtonClick: function (e) {
            if (this.value && this.value.includes("%UID")) {
                var i = this.value.replace('"%UID"', this.record.getContext().uid);
                e.preventDefault(), new view_dialogs.SelectCreateDialog(this, {
                    title: _t("Selected records"),
                    res_model: this._domainModel,
                    domain: i,
                    no_create: !0,
                    readonly: !0,
                    disable_multiple_selection: !0
                }).open()
            } else this._super.apply(this, arguments)
        }
    });

});