# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import requests
import base64
import json
from odoo import models, api, fields
from odoo.osv import expression
from werkzeug.urls import url_join
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pyfcm import FCMNotification
import pprint
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class SocialPostBIT(models.Model):
    _inherit = 'social.post'

    display_bit_preview = fields.Boolean('Display BIT Preview', compute='_compute_display_bit_preview')
    bit_preview = fields.Html('BIT Preview', compute='_compute_bit_preview')
    social_groups_ids = fields.Many2many("social.partner.group","social_groups_post",string="Social Groups")
    social_partner_ids = fields.Many2many("res.partner","social_partner_post",string="Social Partners")
    like_partner_ids = fields.Many2many("res.partner","social_partner_post_like",string="Likes")
    is_bit_post = fields.Boolean("Is Bit Post?")
    message = fields.Text("Message", required=True, translate=True)

    @api.constrains('image_ids')
    def _check_image_ids_mimetype(self):
        for social_post in self:
            if not  social_post.is_bit_post:
                if any(not image.mimetype.startswith('image') for image in social_post.image_ids):
                    raise UserError(_('Uploaded file does not seem to be a valid image.'))
    

    @api.onchange('social_groups_ids')
    def social_groups(self):
        if self.social_groups_ids:
            partners = []
            for record in self.social_groups_ids:
                partners.extend(record.partner_ids.ids) 
            self.social_partner_ids = [(6,0,partners)] 
        else:
            self.social_partner_ids = False

    @api.onchange('account_ids')
    def social_account(self):
        account_id = self.env.ref("dcm_customization.social_account_bit")
        if account_id.id in self.account_ids.ids:
            self.is_bit_post = True
        else:
            self.is_bit_post = False

    def get_post_api(self,partner_id=False):
        _logger.info("Get Post Records From mobile partner_id:%s"%partner_id)
        if partner_id:
            data = []
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not self:
                partner_browse = self.env["res.partner"].browse(int(partner_id))
                posts = self.with_context(lang=partner_browse.lang).search([('social_partner_ids','in',[int(partner_id)]),('state','=','posted')])
            else:
                posts = self
            for post in posts:
                if post.utm_campaign_id:
                    image_url = url_join(base_url,'/web/myimage/utm.campaign/%s/image_128'%post.utm_campaign_id.id)
                    post_date = post.utm_campaign_id.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    post_owner = post.utm_campaign_id.user_id.name
                    post_name = post.utm_campaign_id.name
                else:
                    image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_128'%post.create_uid.partner_id.id)
                    post_date = post.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    post_owner = post.create_uid.partner_id.name
                    post_name = post.create_uid.name
                comments = post.getComments()
                media_ids = post.getMedia()
                data.append({
                    'id':post.id,
                    'name':post_name,
                    'date':post_date,
                    'like':True if int(partner_id) in post.like_partner_ids.ids else False,
                    'image':image_url,
                    'message':post.message,
                    'comments':comments,
                    'media_ids':media_ids,
                    'post_owner':post_owner
                    })
            _logger.info("Get Post Records From mobile records:- \n%s"%pprint.pformat(data))
            return {'data':data}
        else:
            return {'data':[]}

    def getMedia(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        media_ids = []
        for media in self.image_ids:
            image_url = url_join(base_url,'/web/content/%s/%s' % (media.id, media.name))
            mimetype = 'image'
            if not media.mimetype.startswith('image'):
                mimetype = 'video'
            media_ids.append({
                'url': image_url,
                'mimetype': mimetype
            })
        return media_ids
    
    def getComments(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        comments = []
        for msg in self.comments_ids:
            image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_1920'%msg.partner_id.id)
            comments.append({'comment':msg.comment,
                             'id':msg.id,
                             'author_name':msg.partner_id.name,
                             'author_image':image_url,
                             'partner_id':msg.partner_id.id,
                             'date':msg.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            })
        return comments
    
    def set_post_like(self,partner_id,method):
        _logger.info("set like Post record %s partner_id:%s , method %s"%(self,partner_id,method))
        if partner_id and self:
            if method == 'like':
                self.write({'like_partner_ids':[(4,int(partner_id))]})
            if method == 'dislike':
                self.write({'like_partner_ids':[(3,int(partner_id))]})
            return True
        else:
            False
    
    def set_post_delete(self,partner_id):
        _logger.info("set delete Post record %s partner_id:%s "%(self,partner_id))
        if partner_id and self:
            self.write({'social_partner_ids':[(3,int(partner_id))]})
            return True    
        else:
            False
            
    def action_post(self):
        res = super(SocialPostBIT,self).action_post()
        self.image_ids.write({'public':True})
        if self.is_bit_post:
            self.send_fcm_push_notification()

    def send_fcm_push_notification(self):
        subject = "New Post from Midar"
        if self.env.user.company_id.fcm_api_key:
            for lang in list(set(self.social_partner_ids.mapped("lang"))):
                partners = self.social_partner_ids.filtered(lambda x: x.lang == lang)
                body = self.with_context(lang=lang).message

                ios_partner_device_ids = self.env['res.partner.token'].search([('partner_id','in',partners.ids)]).filtered(lambda x: x.device_type == "ios")
                android_partner_device_ids = self.env['res.partner.token'].search([('partner_id','in',partners.ids)]).filtered(lambda x: x.device_type == "android")
                if ios_partner_device_ids:
                    device_list = ios_partner_device_ids.mapped("push_token")
                    if device_list:
                        extra_kwargs = {}
                        data_message = {}
                        if self.image_ids:
                            for media in self.image_ids:
                                if media.mimetype.startswith('image'):
                                    base_url = self.env[
                                        'ir.config_parameter'].sudo().get_param('web.base.url')
                                    image_url = url_join(base_url, '/web/content/%s/%s' % (media.id, media.name))
                                    data_message = {"image": image_url}
                                    extra_kwargs = {"mutable_content": True}
                                    break
                        push_service = FCMNotification(api_key=self.env.user.company_id.fcm_api_key)
                        push_service.notify_multiple_devices(registration_ids=device_list,
                                                             message_title=subject,sound="default",
                                                             message_body=body,data_message=data_message,extra_kwargs=extra_kwargs
                                                             )
                if android_partner_device_ids:
                    device_list = android_partner_device_ids.mapped("push_token")
                    if device_list:
                        extra_kwargs = {}
                        extra_notification_kwargs = {}
                        if self.image_ids:
                            for media in self.image_ids:
                                if media.mimetype.startswith('image'):
                                    base_url = self.env[
                                        'ir.config_parameter'].sudo().get_param(
                                        'web.base.url')
                                    image_url = url_join(base_url,
                                                         '/web/content/%s/%s' % (
                                                         media.id, media.name))
                                    extra_kwargs = {"mutable_content": True}
                                    extra_notification_kwargs = {
                                        "image": image_url}
                                    break
                        push_service = FCMNotification(
                            api_key=self.env.user.company_id.fcm_api_key)
                        push_service.notify_multiple_devices(
                            registration_ids=device_list,
                            message_title=subject, sound="default",
                            message_body=body, data_message=data_message,
                            extra_kwargs=extra_kwargs,
                            extra_notification_kwargs=extra_notification_kwargs
                            )


    @api.depends('live_post_ids.is_bit_post')
    def _compute_stream_posts_count(self):
        super(SocialPostBIT, self)._compute_stream_posts_count()
        for post in self:
            bit_post_ids = [bit_post_id for bit_post_id in post.live_post_ids.mapped('is_bit_post') if bit_post_id]
            if bit_post_ids:
                post.stream_posts_count += self.env['social.stream.post'].search_count(
                    [('post_id', '=', post.id)]
                )

    @api.depends('message', 'account_ids.media_id.media_type')
    def _compute_display_bit_preview(self):
        for post in self:
            post.display_bit_preview = post.message and ('bit' in post.account_ids.media_id.mapped('media_type'))

    @api.depends('message', 'scheduled_date', 'image_ids')
    def _compute_bit_preview(self):
        for post in self:
            image_data = []
            for i in post.image_ids:
                image_data.append({'mimetype':i.mimetype,'datas':base64.b64encode(open(i._full_path(i.store_fname), 'rb').read())})
            post.bit_preview = self.env.ref('dcm_customization.bit_preview').render({
                'message': post.message,
                'published_date': post.scheduled_date if post.scheduled_date else fields.Datetime.now(),
                'image_ids':post.image_ids,
                'image_data':image_data,
                # 'images': [
                #     image.datas if not image.id
                #     else base64.b64encode(open(image._full_path(image.store_fname), 'rb').read()) for image in post.image_ids
                # ]
            })

    def unlink(self):
        for record in self:
            stream_post = self.env['social.stream.post'].search([('post_id','=',record.id)])
            stream_post.unlink()
            stream_post = self.env['social.live.post'].search([('post_id','=',record.id)])
            stream_post.unlink()
        return super(SocialPostBIT, self).unlink()    


    @api.depends('image_ids')
    def _compute_image_urls(self):
        """ See field 'help' for more information. """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for post in self:
            if post.is_bit_post:
                post.image_urls = json.dumps([{'url':url_join(base_url,'web/image/%s' % image_id.id), 'mimetype':True if image_id.mimetype.startswith('image') else False,'fullpath':image_id._full_path(image_id.store_fname)} for image_id in post.image_ids])
            else:
                super(SocialPostBIT,self)._compute_image_urls()
    