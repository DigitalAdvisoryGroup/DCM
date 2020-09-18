from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'


    @api.model
    def create(self, vals):
        if vals.get('res_model') and vals.get('res_model') == 'social.post':
            name = vals.get('name').replace(" ", "_")
            vals['name'] = name
        res = super(IrAttachment,self).create(vals)
        return res

    