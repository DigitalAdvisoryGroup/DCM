from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    fcm_api_key = fields.Char('Notification API Key')
    fcm_title_message = fields.Char('Notification Title Message', translate=True)
    fcm_reply_title_message = fields.Char('Reply Notification Title Message', translate=True)
    privacy_policy_url = fields.Char("Accept Privacy and Policy Terms URL")
    upload_limit = fields.Integer("File Upload Limit(MB)")

    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fcm_api_key = fields.Char(related="company_id.fcm_api_key", string='Notification API Key',readonly=False)
    fcm_title_message = fields.Char(related="company_id.fcm_title_message", string='Notification Title Message',readonly=False, translate=True)
    fcm_reply_title_message = fields.Char(related="company_id.fcm_reply_title_message", string='Reply Notification Title Message',readonly=False, translate=True)
    privacy_policy_url = fields.Char("Accept Privacy and Policy Terms URL",related="company_id.privacy_policy_url",readonly=False)
    upload_limit = fields.Integer("File Upload Limit(MB)",related="company_id.upload_limit",readonly=False)