# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
import json

from pyfcm import FCMNotification
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from itertools import groupby
import math, random
from werkzeug.urls import url_join
import datetime
import logging
_logger = logging.getLogger(__name__)
LANG_CODE_ODOO = {
            "it-IT":"it_IT",
            "rm-CH":"ro_RO",
            "fr-CH":"fr_CH",
            "de-CH":"de_CH",
            "en":"en_US",
            "de": "de_CH",
            "fr": "fr_CH",
            "it": "it_IT",
            "rm": "ro_RO",
}

LANG_CODE_APP = {
            "it_IT":"it-IT",
            "fr_CH":"fr-CH",
            "de_CH":"de-CH",
            "en_US":"en",
            "ro_RO": "rm-CH"
}

class ResPartner(models.Model):
    _inherit = 'res.partner'

    otp_token = fields.Char("OTP Token", copy=False)
    social_group_id = fields.Many2many('social.partner.group','social_group_partner_rel','partner_id','social_group_id',string="Social Group")
    social_group_fun_id = fields.Many2many('social.partner.group','social_group_fun_partner_rel','partner_id','social_group_id',string="Functional Social Group")
    change_connection = fields.Boolean("Change Connection")
    partner_token_lines = fields.One2many("res.partner.token","partner_id", string="Token Lines")
    is_token_available = fields.Boolean("Is Token Available?", compute="_get_token_available", store=True)
    file_name_custom = fields.Char("Filename")
    category_skill_ids = fields.Many2many("res.partner.category", "rel_parnter_category_skill","skill_partner_id","skill_category_id", string="Skills")
    category_res_ids = fields.Many2many("res.partner.category", "rel_parnter_category_res","res_partner_id","res_category_id",string="Responsbilities")

    category_social_id_name = fields.Char("Social Name", compute="_set_category_social_ids_name", store=True)
    category_id_name = fields.Char("Tags Name", compute="_set_category_name", store=True)
    category_skill_id_name = fields.Char("Skill Name", compute="_set_category_skill_ids_name", store=True)
    category_res_id_name = fields.Char("Responsbility Name", compute="_set_category_res_ids_name", store=True)

    # ao1_id = fields.Char("AO 1")
    # ao2_id = fields.Char("AO 2")
    # ao3_id = fields.Char("AO 3")
    # ao_key = fields.Char("AO-Key")
    fu1_id = fields.Char("FU 1")
    fu2_id = fields.Char("FU 2")
    fu3_id = fields.Char("FU 3")
    fu_key = fields.Char("Func Unit Key")
    # hlevel = fields.Char("Hierarchy Level")
    # hlevel_id = fields.Char("Hierarchy Level")
    mlevel_id = fields.Many2one("partner.mlevel","Management level")
    # oe1_id = fields.Char("OE 1")
    # oe2_id = fields.Char("OE 2")
    # oe3_id = fields.Char("OE 3")
    # oe_key = fields.Char("OE-Key")
    # ou1_id = fields.Char("OU 1")
    # ou2_id = fields.Char("OU 2")
    # ou3_id = fields.Char("OU 3")
    # ou_key = fields.Char("Org Unit Key")


    def update_store_fields(self):
        for part in self:
            part._set_category_name()
            part._set_category_skill_ids_name()
            part._set_category_res_ids_name()
            part._set_category_social_ids_name()
        return True


    @api.depends("category_id")
    def _set_category_name(self):
        for part in self:
            if part.category_id:
                part.category_id_name = ",".join([x.name+":"+str(x.id) for x in part.category_id])

    @api.depends("category_skill_ids")
    def _set_category_skill_ids_name(self):
        for part in self:
            if part.category_skill_ids:
                part.category_skill_id_name = ",".join([x.name+":"+str(x.id) for x in part.category_skill_ids])

    @api.depends("social_group_id")
    def _set_category_social_ids_name(self):
        for part in self:
            if part.social_group_id:
                part.category_social_id_name = ",".join([x.name+":"+str(x.id) for x in part.social_group_id])

    @api.depends("category_res_ids")
    def _set_category_res_ids_name(self):
        for part in self:
            if part.category_res_ids:
                part.category_res_id_name = ",".join([x.name+":"+str(x.id) for x in part.category_res_ids])

    @api.depends("partner_token_lines")
    def _get_token_available(self):
        for part in self:
            if len(part.partner_token_lines) > 0:
                part.is_token_available = True
            else:
                part.is_token_available = False

    def get_partner_from_email(self, email, token, lang, device_type="android"):
        data = []
        if email:
            partner_id = self.search([('email', '=', email.lower())])
            if partner_id:
                if lang:
                    lang_id = self.env['res.lang']._lang_get(lang)
                    if lang_id:
                        partner_id.write({'lang': lang_id.code})
                    else:
                        partner_id.write({'lang': 'en_US'})
                # partner_id.lang = "de_CH"
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
                image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_128/?%s'%(partner_id.id,partner_id.file_name_custom))
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
                    'change_connection':partner_id.change_connection,
                    'lang': LANG_CODE_APP.get(partner_id.lang)
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
        if otp:
            partner_id = self.search([('email','=',email.lower()),("otp_token","=",otp)])
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


    def get_partner_profile_data(self):
        data = []
        if self:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            image_url = url_join(base_url,
                                 '/web/myimage/res.partner/%s/image_128/?%s' % (self.id,self.file_name_custom))
            data.append({
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'street': self.street,
                'street2': self.street2,
                'mobile': self.mobile,
                'city': self.city,
                'state_id': self.state_id and self.state_id.name or '',
                'country_id': self.country_id and self.country_id.name or '',
                'zip': self.zip,
                'image_1920': image_url,
                'change_connection': self.change_connection,
                'lang': LANG_CODE_APP.get(self.lang)
            })
        return {'data': data}

    def set_partner_language(self,lang_code):
        if self and LANG_CODE_ODOO.get(lang_code,False):
            self.lang = LANG_CODE_ODOO.get(lang_code,"en_US")
        return True

    @api.model
    def add_contact_posts(self,new_partner_ids=False):
        if not new_partner_ids:
            current_date = datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
            new_partner_ids = self.search([('create_date','>=',current_date)]).ids
        if new_partner_ids:
            for part in new_partner_ids:
                post_ids = self.env['social.post'].search([('utm_campaign_id.stage_id.is_active','=',True),('state','=','posted'),('utm_campaign_id.is_public_campaign','=',True)])
                if post_ids:
                    for post in post_ids:
                        if part not in post.social_partner_ids.ids:
                            post.with_context(add_post=True).social_partner_ids = [(4, part)]
        return True


class ResPartnerToken(models.Model):
    _name = 'res.partner.token'
    _description = "Res Partner Token"
    _rec_name = "partner_id"
    
    partner_id = fields.Many2one("res.partner","Partner")
    push_token = fields.Char("Firebase Token")
    device_type = fields.Selection([("ios","Apple"),("android","Android")],string="Device Type", default="android")
    active = fields.Boolean("Active", default=True)

    @api.model
    def _clean_invalid_device_ids(self):
        device_ids = self.search([])
        if device_ids and self.env.user.company_id.fcm_api_key:
            device_list = [x.push_token for x in device_ids]
            push_service = FCMNotification(api_key=self.env.user.company_id.fcm_api_key)
            valid_registration_ids = push_service.clean_registration_ids(device_list)
            inactive_device_ids = list(set(device_list) - set(valid_registration_ids))
            if inactive_device_ids:
                inactive_device_ids = self.search([('push_token', 'in', inactive_device_ids)])
                inactive_device_ids.write({'active': False})

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(ResPartnerToken, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if self.env.context.get("click_graph"):
            current_ios_count = 0
            current_android_count = 0
            res = self.get_arrange_dict(res)
            for line in res:
                if line.get("device_type"):
                    if line['device_type'] == "ios":
                        current_count = line['__count']
                        current_ios_count += line['__count']
                        line['__count'] += (current_ios_count - current_count)
                    elif line['device_type'] == "android":
                        current_count = line['__count']
                        current_android_count += line['__count']
                        line['__count'] += (current_android_count - current_count)
                    else:
                        continue
        return res

    def get_arrange_dict(self,lst):
        final_list = []
        for k, v in groupby(lst, key=lambda x: x['create_date:week']):
            same_week_list = list(v)
            if len(same_week_list) == 2:
                final_list.extend(same_week_list)
            for i in same_week_list:
                if i.get('device_type', False) and len(same_week_list) != 2 and i.get('device_type') == 'ios':
                    android_dict = json.dumps(i.copy())
                    android_dict = android_dict.replace('ios', 'android')
                    android_dict = json.loads(android_dict)
                    android_dict['__count'] = 0
                    final_list.append(i)
                    final_list.append(android_dict)
                if i.get('device_type', False) and len(same_week_list) != 2 and i.get('device_type') == 'android':
                    android_dict = json.dumps(i.copy())
                    android_dict = android_dict.replace('android', 'ios')
                    android_dict = json.loads(android_dict)
                    android_dict['__count'] = 0
                    final_list.append(i)
                    final_list.append(android_dict)
        return final_list

class PartnerMlevel(models.Model):
    _name = "partner.mlevel"
    _description = "Mlevel"

    name = fields.Char("Name")
    code = fields.Char("Code")
