
from odoo import models, api, fields
from pyfcm import FCMNotification
from werkzeug.urls import url_join
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
    rating = fields.Integer("Rating")
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
        filename = vals.get("filename") and vals.pop("filename") or False
        file_content = vals.get("content") and vals.pop("content") or False
        _logger.info("-----comment-------filename------%s-",filename)
        res = super(SocialBitComments,self).create(vals)
        if filename and file_content:
            attachment_id = self.env['ir.attachment'].create({
                'name': filename,
                'res_id': res.id,
                'res_model': res._name,
                'datas': file_content,
                'type': 'binary',
                'public': True
            })
            if attachment_id:
                res.image_ids = attachment_id.ids
        if res.parent_id and res.parent_id.record_type == 'comment' and res.record_type == 'comment':
            if (self.env.user.company_id.fcm_api_key and self.env.user.company_id.fcm_title_message):
                body = res.comment
                # subject = self.env.user.company_id.with_context(lang=res.parent_id.partner_id.lang).fcm_reply_title_message
                subject = "New Reply From %s"%(res.partner_id.name)
                device_list = self.env['res.partner.token'].search([('partner_id','=',res.parent_id.partner_id.id)]).mapped("push_token")
                if device_list:
                    push_service = FCMNotification(api_key=self.env.user.company_id.fcm_api_key)
                    push_service.notify_multiple_devices(registration_ids=device_list,
                                                         message_title=subject,sound="default",
                                                         message_body=body
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