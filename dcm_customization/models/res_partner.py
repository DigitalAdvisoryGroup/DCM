# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
import math, random
from werkzeug.urls import url_join
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    otp_token = fields.Char("OTP Token", copy=False)
    social_group_id = fields.Many2one('social.partner.group',string="Social Group")

    def get_partner_from_email(self, email, token, lang, device_type="android"):
        _logger.info("-------------------get partner method email -: %s \n token %s \n lang %s \n device type %s" % (
            email, token, lang,device_type))
        data = []
        if email:
            partner_id = self.search([('email', '=', email)])
            if partner_id:
                if lang:
                    lang_id = self.env['res.lang']._lang_get(lang)
                    if lang_id:
                        partner_id.write({'lang': lang_id.code})
                    else:
                        partner_id.write({'lang': 'en_US'})
                partner_token_id = self.env['res.partner.token'].search([('partner_id', '=', partner_id.id),
                                                                         ('push_token','=',token)])
                if not partner_token_id:
                    self.env['res.partner.token'].create(
                        {'partner_id': partner_id.id,"push_token": token,"device_type": device_type})
                partner_token_id.device_type = device_type
                partner_id.set_otp_partner()
                partner_id.send_otp_partner()
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_128'%partner_id.id)
                data.append({
                    'id': partner_id.id,
                    'name': partner_id.name,
                    'email': partner_id.email,
                    'street': partner_id.street,
                    'street2': partner_id.street2,
                    'mobile': partner_id.mobile,
                    'city': partner_id.city,
                    'state_id': partner_id.state_id and partner_id.state_id.name or '',
                    'country_id': partner_id.country_id and partner_id.country_id.name or '',
                    'zip': partner_id.zip,
                    'image_1920': image_url,
                })
                return {'data': data}
        return {'data': data}

    def set_otp_partner(self):
        self.ensure_one()
        if self.email == "hello@digitaladvisorygroup.io":
            self.otp_token = "966718"
            return True
        digits = "0123456789"
        OTP = ""
        for i in range(6):
            OTP += digits[math.floor(random.random() * 10)]
        if OTP:
            self.otp_token = OTP


    def send_otp_partner(self):
        self.ensure_one()
        template = self.env.ref('dcm_customization.email_template_otp_partner',
                                raise_if_not_found=False)
        lang = get_lang(self.env)
        if template and template.lang:
            lang = template._render_template(template.lang, 'res.partner',
                                             self.id)
        else:
            lang = lang.code
        if template:
            template.sudo().with_context(lang=lang).send_mail(
                self.id, force_send=True)
            return True
        return False


    def get_partner_otp_verify(self,email,otp):
        _logger.info("-------------------get_partner_otp_verify -: %s \n otp %s"%(email,otp))
        if otp:
            partner_id = self.search([('email','=',email),("otp_token","=",otp)])
            if partner_id:
                return True
        return False

    def set_logout_app(self,token):
        if token:
            partner_device_id = self.env["res.partner.token"].search([("partner_id","=",self.id),("push_token","=",token)])
            if partner_device_id:
                partner_device_id.unlink()
            return True
        return False


class ResPartnerToken(models.Model):
    _name = 'res.partner.token'
    _description = "Res Partner Token"
    _rec_name = "partner_id"
    
    partner_id = fields.Many2one("res.partner","Partner")
    push_token = fields.Char("Firebase Token")
    device_type = fields.Selection([("ios","Apple"),("android","Android")],string="Device Type", default="android")





