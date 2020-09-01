# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
import math, random
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    otp_token = fields.Char("OTP Token", copy=False)

    def get_partner_from_email(self,email,token, lang):
        _logger.info("-------------------get partner method email -: %s \n token %s \n lang %s"%(email,token,lang))
        if email:
            partner_id = self.search([('email','=',email)])
            if partner_id:
                if lang:
                    lang_id = self.env['res.lang']._lang_get(lang)
                    if lang_id:
                        partner_id.write({'lang':lang_id.code})
                    else:
                        partner_id.write({'lang':'en_US'})
                website_visitor = self.env['website.visitor'].search([('partner_id','=',partner_id.id)])
                if not website_visitor:
                    self.env['website.visitor'].create({'partner_id': partner_id.id,
                            "push_token":token ,
                            "name": partner_id.name
                            }
                        )
                else:
                    website_visitor.write({'push_token':token})       
                partner_id.set_otp_partner()
                partner_id.send_otp_partner()
                return partner_id.id
        return False

    def set_otp_partner(self):
        self.ensure_one()
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






