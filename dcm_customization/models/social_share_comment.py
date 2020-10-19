
from odoo import models, api, fields
from pyfcm import FCMNotification
from werkzeug.urls import url_join
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)

class SocialBitComments(models.Model):
    _name = 'social.bit.comments'
    _description = "Social Bit Comments"
    _rec_name = "partner_id"
    _order = "id desc"

    partner_id = fields.Many2one("res.partner",string="Partner")
    post_id  = fields.Many2one("social.post",string="Social Post")
    utm_campaign_id = fields.Many2one('utm.campaign',related=False, string="Campaign", store=True)
    comment = fields.Text("Comments")
    record_type = fields.Selection([('com_like','Comment Like'),('com_dislike','Comment Dislike'),('like','Like'),('dislike','Dislike'),('comment','Comment'),('share','Share'),('rating','Rating'),("post_delete","Post Delete")],string="Type", default="comment")
    rating = fields.Integer("Rating",group_operator="avg")
    parent_id = fields.Many2one('social.bit.comments',string="Parent")
    child_ids = fields.One2many('social.bit.comments','parent_id',string="Childs",domain=[('record_type','=','comment')])
    child_comlike_ids = fields.One2many('social.bit.comments','parent_id',string="Comment Like",domain=[('record_type','=','com_like')])
    child_comdislike_ids = fields.One2many('social.bit.comments','parent_id',string="Comment DisLike",domain=[('record_type','=','com_dislike')])
    image_ids = fields.Many2many('ir.attachment', string='Attach Images')

    @api.model
    def create(self, vals):
        if not vals.get('utm_campaign_id'):
            post_id = self.env['social.post'].browse(vals.get('post_id'))
            if post_id:
                vals['utm_campaign_id'] = post_id.utm_campaign_id.id
        filename = False
        file_content = False
        if "filename" in vals:
            filename = vals.pop("filename")
        if "content" in vals:
            file_content = vals.pop("content")
        res = super(SocialBitComments,self).create(vals)
        if filename and file_content:
            attachment_id = self.env['ir.attachment'].create({
                'name': filename.strip("/"),
                'res_id': res.id,
                'res_model': res._name,
                'datas': file_content,
                'type': 'binary',
                'public': True
            })
            if attachment_id:
                res.image_ids = attachment_id.ids
        if res.parent_id and res.parent_id.record_type == 'comment' and res.record_type == 'comment':
            if (self.env.user.company_id.fcm_api_key and self.env.user.company_id.fcm_reply_title_message):
                body = res.comment
                subject = self.env.user.company_id.with_context(lang=res.parent_id.partner_id.lang).fcm_reply_title_message+" %s"%(res.partner_id.name)
                # subject = "New Reply From %s"%(res.partner_id.name)
                # device_list = self.env['res.partner.token'].search([('partner_id','=',res.parent_id.partner_id.id)]).mapped("push_token")
                token_id = self.env['res.partner.token'].search([('partner_id','=',res.parent_id.partner_id.id)])
                ios_token_id = token_id.filtered(lambda x: not x.device_type == "ios")
                android_token_id = token_id.filtered(lambda x: not x.device_type != "ios")
                push_service = FCMNotification(
                    api_key=self.env.user.company_id.fcm_api_key)
                if ios_token_id:
                    push_service.notify_multiple_devices(registration_ids=ios_token_id.mapped("push_token"),
                                                         message_title=subject,sound="default",
                                                         message_body=body,click_action="%s,%s"%(res.post_id.id,res.parent_id.id)
                                                         )
                else:
                    push_service.notify_multiple_devices(
                        registration_ids=android_token_id.mapped("push_token"),
                        sound="default",
                        # message_title=subject,message_body=body,
                        # extra_notification_kwargs={"post_id": str(res.post_id.id), "comment_id": str(res.parent_id.id)}
                        data_message={"notification": {"post_id": res.post_id.id, "comment_id": res.parent_id.id,
                                      "message_title": subject,"click_action":"COMMENTACTIVITY",
                                      "message_body": body}}
                        )
        return res

    def getCommentMedia(self):
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


    def get_reply_for_comment(self):
        comments = []
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        if self:
            image_url = url_join(base_url,
                                 '/web/myimage/res.partner/%s/image_128' % self.partner_id.id)
            child_comments = []
            for c_comment in self.child_ids:
                c_image_url = url_join(base_url,
                                       '/web/myimage/res.partner/%s/image_128' % c_comment.partner_id.id)
                child_comments.append({'comment': c_comment.comment,
                                       'id': c_comment.id,
                                       'author_name': c_comment.partner_id.name,
                                       'author_image': c_image_url,
                                       'partner_id': c_comment.partner_id.id,
                                       'media_ids': c_comment.getCommentMedia(),
                                       'date': c_comment.create_date.strftime(
                                           DEFAULT_SERVER_DATETIME_FORMAT)
                                       })
            comments.append({'comment': self.comment,
                             'id': self.id,
                             'author_name': self.partner_id.name,
                             'author_image': image_url,
                             'partner_id': self.partner_id.id,
                             'date': self.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                             'child_comments': child_comments,
                             'replay_counter': len(child_comments),
                             'media_ids': self.getCommentMedia(),
                             'like_counter': len(self.child_comlike_ids),
                             'dislike_counter': len(self.child_comdislike_ids),
                             'comment_like': True if self.child_comlike_ids.filtered(
                                 lambda a: a.partner_id.id == int(self.partner_id.id)) else False,
                             'comment_dislike': True if self.child_comdislike_ids.filtered(
                                 lambda a: a.partner_id.id == int(
                                     self.partner_id.id)) else False,
                             'upload_limit': self.env.user.company_id.upload_limit
                             })
        return {"data": comments}


    def set_comment_like(self, partner_id):
        if self:
            child_comdislike_ids = self.env['social.bit.comments'].search(
                [('parent_id','=',self.id),
                 ('partner_id','=',int(partner_id)),
                 ('record_type','=','com_dislike')])
            child_comlike_ids = self.env['social.bit.comments'].search(
                [('parent_id', '=', self.id),
                 ('partner_id', '=', int(partner_id)),
                 ('record_type', '=', 'com_like')])
            if child_comdislike_ids:
                child_comdislike_ids.unlink()
            if not child_comlike_ids:
                self.env['social.bit.comments'].create(
                    {'post_id': self.post_id.id, 'partner_id': int(partner_id),"parent_id": self.id,
                     'record_type': "com_like"})
            return True
        return False

    def set_comment_dislike(self,partner_id):
        if self:
            child_comdislike_ids = self.env['social.bit.comments'].search(
                [('parent_id', '=', self.id),
                 ('partner_id', '=', int(partner_id)),
                 ('record_type', '=', 'com_dislike')])
            child_comlike_ids = self.env['social.bit.comments'].search(
                [('parent_id', '=', self.id),
                 ('partner_id', '=', int(partner_id)),
                 ('record_type', '=', 'com_like')])
            if child_comlike_ids:
                child_comlike_ids.unlink()
            if not child_comdislike_ids:
                self.env['social.bit.comments'].create(
                    {'post_id': self.post_id.id, 'partner_id': int(partner_id),
                     "parent_id": self.id,
                     'record_type': "com_dislike"})
            return True

            return True
        return False


