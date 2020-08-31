# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import requests
import base64

from odoo import models, api, fields
from odoo.osv import expression
from werkzeug.urls import url_join
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pyfcm import FCMNotification
import pprint
import logging
_logger = logging.getLogger(__name__)


class SocialPostBIT(models.Model):
    _inherit = 'social.post'

    display_bit_preview = fields.Boolean('Display BIT Preview', compute='_compute_display_bit_preview')
    bit_preview = fields.Html('BIT Preview', compute='_compute_bit_preview')
    social_groups_ids = fields.Many2many("social.partner.group","social_groups_post",string="Social Groups")
    social_partner_ids = fields.Many2many("res.partner","social_partner_post",string="Social Partners")
    like_partner_ids = fields.Many2many("res.partner","social_partner_post_like",string="Likes")
    is_bit_post = fields.Boolean("Is Bit Post?")
    

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

    def get_post_api(self,partner_id):
        _logger.info("Get Post Records From mobile partner_id:%s"%partner_id)
        if partner_id:
            posts = self.search([('social_partner_ids','in',[int(partner_id)]),('state','=','posted')])
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            data = []
            for post in posts:
                image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_1920'%post.create_uid.partner_id.id)
                comments = post.getComments()
                data.append({
                    'id':post.id,
                    'name':post.create_uid.partner_id.name,
                    'date':post.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'like':True if int(partner_id) in post.like_partner_ids.ids else False,
                    'image':image_url,
                    'message':post.message,
                    'comments':comments
                    })
            _logger.info("Get Post Records From mobile records:- \n%s"%pprint.pformat(data))
            return {'data':data}        
        else:
            False
    
    def getComments(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        comments = []
        for msg in self.comments_ids:
            image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_1920'%msg.partner_id.id)
            comments.append({'comment':msg.comment,
                             'id':msg.id,
                             'author_name':msg.partner_id.name,
                             'author_image':image_url,
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
        if self.is_bit_post:
            self.send_fcm_push_notification()

    def send_fcm_push_notification(self):
        subject = "New Post from BIT"
        body = self.message
        if self.env.user.company_id.fcm_api_key:
            device_list = []
            for device in self.social_partner_ids:
                visitor_id = self.env['website.visitor'].search([('partner_id','=',device.id)],limit=1)
                if visitor_id.push_token:
                    device_list.append(visitor_id.push_token)
            if device_list:
                push_service = FCMNotification(api_key=self.env.user.company_id.fcm_api_key)
                push_service.notify_multiple_devices(registration_ids=device_list,
                                                              message_title=subject, message_body=body)

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
            post.bit_preview = self.env.ref('dcm_customization.bit_preview').render({
                'message': post.message,
                'published_date': post.scheduled_date if post.scheduled_date else fields.Datetime.now(),
                'images': [
                    image.datas if not image.id
                    else base64.b64encode(open(image._full_path(image.store_fname), 'rb').read()) for image in post.image_ids
                ]
            })

    def unlink(self):
        for record in self:
            stream_post = self.env['social.stream.post'].search([('post_id','=',record.id)])
            stream_post.unlink()
            stream_post = self.env['social.live.post'].search([('post_id','=',record.id)])
            stream_post.unlink()
        return super(SocialPostBIT, self).unlink()    
