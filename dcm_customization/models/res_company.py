from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    fcm_api_key = fields.Char('Server API Key')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fcm_api_key = fields.Char(related="company_id.fcm_api_key", string='Server API Key',readonly=False)