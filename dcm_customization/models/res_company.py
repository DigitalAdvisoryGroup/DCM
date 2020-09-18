from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    fcm_api_key = fields.Char('Notification API Key')
    fcm_title_message = fields.Char('Notification Title Message', translate=True)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fcm_api_key = fields.Char(related="company_id.fcm_api_key", string='Notification API Key',readonly=False)
    fcm_title_message = fields.Char(related="company_id.fcm_title_message", string='Notification Title Message',readonly=False, translate=True)