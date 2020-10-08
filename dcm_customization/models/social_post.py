# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import requests
import base64
import json
from odoo import models, api, fields, _
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
    _rec_name = ""

    display_bit_preview = fields.Boolean('Display BIT Preview', compute='_compute_display_bit_preview')
    bit_preview = fields.Html('BIT Preview', compute='_compute_bit_preview')
    social_groups_ids = fields.Many2many("social.partner.group","social_groups_post",string="Social Groups")
    social_partner_ids = fields.Many2many("res.partner","social_partner_post",string="Social Partners")
    is_bit_post = fields.Boolean("Is Bit Post?")
    message = fields.Text("Message", required=True, translate=True)
    share_ids = fields.One2many('social.bit.comments', 'post_id',
                                string="Shares",
                                domain=[('record_type','=','share')])
    comments_ids = fields.One2many('social.bit.comments', 'post_id',
                                   string="Comments",
                                   domain=[('record_type','=','comment')])
    like_ids = fields.One2many('social.bit.comments', 'post_id',
                                   string="Likes",
                                   domain=[('record_type', '=', 'like')])
    dislike_ids = fields.One2many('social.bit.comments', 'post_id',
                                   string="Dislike",
                                   domain=[('record_type', '=', 'dislike')])
    recipients_ids = fields.Many2many('res.partner',string="Recipients")

    @api.constrains('image_ids')
    def _check_image_ids_mimetype(self):
        for social_post in self:
            if not  social_post.is_bit_post:
                if any(not image.mimetype.startswith('image') for image in social_post.image_ids):
                    raise UserError(_('Uploaded file does not seem to be a valid image.'))
    

    @api.onchange('social_groups_ids','utm_campaign_id','recipients_ids')
    def social_groups(self):
        if self.social_groups_ids or self.recipients_ids:
            partners = []
            # opt_out_users = self.utm_campaign_id.opt_out_partner_ids.ids
            partners = list(set(self.social_groups_ids.mapped('partner_ids').ids +self.social_groups_ids.mapped('child_ids').mapped('partner_ids').ids + self.recipients_ids.ids))

            # partners = [p for p in partners if p not in opt_out_users]
            self.social_partner_ids = [(6,0,partners)] 
            return {'domain':{'recipients_ids':[('id','not in',self.social_groups_ids.mapped('child_ids').mapped('partner_ids').ids)]}}
        else:
            self.social_partner_ids = False
            return {}

    @api.onchange('account_ids')
    def social_account(self):
        account_id = self.env.ref("dcm_customization.social_account_bit")
        if account_id.id in self.account_ids.ids:
            self.is_bit_post = True
        else:
            self.is_bit_post = False

    def get_post_api(self,partner_id=False, limit=None,offset=0):
        _logger.info("Get Post Records From mobile partner_id:%s"%partner_id)
        _logger.info("post limit:%s"%limit)
        _logger.info("post offset:%s"%offset)
        if partner_id:
            data = []
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            partner_browse = self.env["res.partner"].browse(int(partner_id))
            if not self:
                posts = self.with_context(lang=partner_browse.lang).search([('social_partner_ids','in',[int(partner_id)]),('state','=','posted'),('utm_campaign_id.stage_id.is_active','=',True)], limit=limit,offset=offset)
                _logger.info("------post---------%s",posts)
            else:
                posts = self.with_context(lang=partner_browse.lang)
            for post in posts:
                like = self.env['social.bit.comments'].search_count([('post_id','=',post.id),('record_type','=','like'),('partner_id','=',int(partner_id))])
                dislike = self.env['social.bit.comments'].search_count([('post_id','=',post.id),('record_type','=','dislike'),('partner_id','=',int(partner_id))])
                data.append({
                    'id':post.id,
                    'name':post.utm_campaign_id.name,
                    'date':post.utm_campaign_id and post.utm_campaign_id.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT) or post.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'like':True if like else False,
                    'dislike':True if dislike else False,
                    'image':url_join(base_url,'/web/myimage/utm.campaign/%s/image_128'%post.utm_campaign_id.id),
                    'message':post.message,
                    'comments':post.getComments(partner_id),
                    'media_ids':post.getMedia(),
                    'post_owner':post.utm_campaign_id.user_id.name,
                    'utm_campaign_id': post.utm_campaign_id.id,
                    'utm_campaign_required': post.utm_campaign_id.is_mandatory_campaign,
                    'rating':round(post.utm_campaign_id.avg_rating,1),
                    'upload_limit': self.env.user.company_id.upload_limit,
                    'total_like_count': len(post.like_ids),
                    'total_dislike_count': len(post.dislike_ids),
                    'total_comment_count': len(post.comments_ids),
                    'total_share_count': len(post.share_ids),
                })
            _logger.info("Get Post Records From mobile records:- \n%s"%pprint.pformat(data))
            return {'data':data}
        else:
            return {'data':[]}

    def getMedia(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        media_ids = []
        for media in self.image_ids:
            mimetype = media.mimetype
            if media.mimetype:
                mimetype = media.mimetype.split('/')[0]
                if media.mimetype in ['application/pdf']:
                    mimetype = "pdf"
                if media.mimetype in ['vnd.openxmlformats-officedocument.presentationml.presentation']:
                    mimetype = "ppt"
                if media.mimetype in ['application/vnd.ms-excel']:
                    mimetype = "doc"
            media_ids.append({
                'url': url_join(base_url,'/web/content/%s/%s' % (media.id, media.name)),
                'mimetype': mimetype
            })
        return media_ids

    def getComments(self,partner_id):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        comments = []
        for msg in self.comments_ids.filtered(lambda a:not a.parent_id):
            image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_128'%msg.partner_id.id)
            child_comments = []
            for c_comment in msg.child_ids:
                c_image_url = url_join(base_url,'/web/myimage/res.partner/%s/image_128'%c_comment.partner_id.id)
                child_comments.append({'comment':c_comment.comment,
                             'id':c_comment.id,
                             'author_name':c_comment.partner_id.name,
                             'author_image':c_image_url,
                             'partner_id':c_comment.partner_id.id,
                             'media_ids': c_comment.getCommentMedia(),
                             'date':c_comment.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            })

            comments.append({'comment':msg.comment,
                             'id':msg.id,
                             'author_name':msg.partner_id.name,
                             'author_image':image_url,
                             'partner_id':msg.partner_id.id,
                             'date':msg.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                             'child_comments':child_comments,
                             'replay_counter':len(child_comments),
                             'media_ids': msg.getCommentMedia(),
                             'like_counter':len(msg.child_comlike_ids),
                             'dislike_counter':len(msg.child_comdislike_ids),
                             'comment_like':True if msg.child_comlike_ids.filtered(lambda a:a.partner_id.id == int(partner_id)) else False,
                             'comment_dislike':True if msg.child_comdislike_ids.filtered(lambda a:a.partner_id.id == int(partner_id)) else False
                            })
        return comments
    
    def set_post_like(self,partner_id):
        _logger.info("set like Post record %s partner_id:%s"%(self,partner_id))
        if partner_id and self:
            like_existing_record = self.env['social.bit.comments'].search(
                [('post_id', '=', self.id),
                 ('partner_id', '=', int(partner_id)),
                 ('record_type', '=', 'like')])
            dislike_existing_record = self.env['social.bit.comments'].search(
                [('post_id', '=', self.id),
                 ('partner_id', '=', int(partner_id)),
                 ('record_type', '=', 'dislike')])
            if dislike_existing_record:
                dislike_existing_record.unlink()
            if not like_existing_record:
                self.env['social.bit.comments'].create(
                    {'post_id': self.id, 'partner_id': int(partner_id),
                     'record_type': "like"})
            return True
        return False

    def set_post_dislike(self,partner_id):
        _logger.info("set Dislike Post record %s partner_id:%s"%(self,partner_id))
        if partner_id and self:
            dislike_existing_record = self.env['social.bit.comments'].search(
                [('post_id','=',self.id),
                 ('partner_id','=',int(partner_id)),
                 ('record_type','=','dislike')])
            like_existing_record = self.env['social.bit.comments'].search(
                [('post_id', '=', self.id),
                 ('partner_id', '=', int(partner_id)),
                 ('record_type', '=', 'like')])
            if like_existing_record:
                like_existing_record.unlink()
            if not dislike_existing_record:
                self.env['social.bit.comments'].create({'post_id':self.id,'partner_id':int(partner_id),'record_type':"dislike"})
            return True
        return False
    
    def set_post_delete(self,partner_id, delete_flag="post"):
        _logger.info("set delete Post record %s partner_id:%s "%(self,partner_id))
        if partner_id and self:
            if delete_flag == "post":
                self.write({'social_partner_ids': [(3, int(partner_id))]})
                vals = {"partner_id": int(partner_id),
                        "post_id": self.id,
                        "record_type": "post_delete"}
                self.env["social.bit.comments"].create(vals)
            else:
                self.utm_campaign_id.write({'opt_out_partner_ids':[(4,int(partner_id))]})
            return True    
        else:
            False
            
    def action_post(self):
        res = super(SocialPostBIT,self).action_post()
        self.image_ids.write({'public':True})
        if self.is_bit_post:
            self.send_fcm_push_notification()
        return res

    def send_fcm_push_notification(self):
        if not (self.env.user.company_id.fcm_api_key and self.env.user.company_id.fcm_title_message):
            raise UserError(_('Please add FCM Server key and Notificaiton Title Message.'))
        for lang in list(set(self.social_partner_ids.mapped("lang"))):
            partners = self.social_partner_ids.filtered(lambda x: x.lang == lang)
            body = self.with_context(lang=lang).message
            subject = self.env.user.company_id.with_context(lang=lang).fcm_title_message
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
                    resp = push_service.notify_multiple_devices(registration_ids=device_list,
                                                         message_title=subject,sound="default",click_action="0",
                                                         message_body=body,data_message=data_message,extra_kwargs=extra_kwargs
                                                         )
                    _logger.info("--------FCM-----ios------------%s",resp)
            if android_partner_device_ids:
                device_list = android_partner_device_ids.mapped("push_token")
                if device_list:
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
                                extra_notification_kwargs = {
                                    "image": image_url}
                                break
                    push_service = FCMNotification(
                        api_key=self.env.user.company_id.fcm_api_key)
                    resp = push_service.notify_multiple_devices(
                        registration_ids=device_list,
                        message_title=subject, sound="default",
                        message_body=body,
                        extra_notification_kwargs=extra_notification_kwargs
                        )
                    _logger.info("--------FCM-----android------------%s", resp)


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
    