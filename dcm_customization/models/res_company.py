from odoo import api, fields, models
from werkzeug.urls import url_join

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    fcm_api_key = fields.Char('Notification API Key')
    fcm_title_message = fields.Char('Notification Title Message', translate=True)
    fcm_reply_title_message = fields.Char('Reply Notification Title Message', translate=True)
    privacy_policy_url = fields.Char("Accept Privacy and Policy Terms URL")
    upload_limit = fields.Integer("File Upload Limit(MB)")
    iframe_acess_token = fields.Char("Iframe Token")
    iframe_url = fields.Char("Iframe URL", compute="_set_iframe_url", store=True)

    @api.depends("iframe_acess_token")
    def _set_iframe_url(self):
        for rec in self:
            if rec.iframe_acess_token:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                rec.iframe_url = url_join(base_url,'/midardir?token=%s'%(rec.iframe_acess_token))
            else:
                rec.iframe_url = False

    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fcm_api_key = fields.Char(related="company_id.fcm_api_key", string='Notification API Key',readonly=False)
    fcm_title_message = fields.Char(related="company_id.fcm_title_message", string='Notification Title Message',readonly=False, translate=True)
    fcm_reply_title_message = fields.Char(related="company_id.fcm_reply_title_message", string='Reply Notification Title Message',readonly=False, translate=True)
    privacy_policy_url = fields.Char("Accept Privacy and Policy Terms URL",related="company_id.privacy_policy_url",readonly=False)
    upload_limit = fields.Integer("File Upload Limit(MB)",related="company_id.upload_limit",readonly=False)
    iframe_acess_token = fields.Char("Iframe Access Token",related="company_id.iframe_acess_token",readonly=False)
    iframe_url = fields.Char("Iframe Access Token",related="company_id.iframe_url")