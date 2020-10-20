# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import dateutil.parser
import requests
import urllib.parse

from odoo import api, models, fields
from werkzeug.urls import url_join
import json

class SocialStreamPostBIT(models.Model):
    _inherit = 'social.stream.post'

    # bit_author_id = fields.Many2one('res.users',string="But Users")
    post_id = fields.Many2one("social.post","Post")
    bit_post_likes = fields.Integer("Bit Post Likes",compute="compute_bit_post_like",store=True)
    bit_post_comments = fields.Integer("Bit Post Comments",compute="compute_bit_post_like",store=True)
    bit_post_share = fields.Integer("Bit Post Share",compute="compute_bit_post_like",store=True)
    image_ids = fields.Many2many('ir.attachment', string='Attach Images',compute="compute_image_ids")

    def compute_image_ids(self):
        for record in self:
            record.image_ids = record.post_id.image_ids

    @api.depends('post_id.comments_ids','post_id.share_ids')
    def compute_bit_post_like(self):
        for record in self:
            record.bit_post_likes = self.env['social.bit.comments'].search_count([('post_id','=',record.post_id.id),('record_type','=','like')])
            record.bit_post_comments = len(record.post_id.comments_ids)
            record.bit_post_share = len(record.post_id.share_ids)
            

    def _compute_author_link(self):
        bit_posts = self.filtered(lambda post: post.stream_id.media_id.media_type == 'bit')
        super(SocialStreamPostBIT, (self - bit_posts))._compute_author_link()

        for post in bit_posts:
            post.author_link = False

    def _compute_post_link(self):
        bit_posts = self.filtered(lambda post: post.stream_id.media_id.media_type == 'bit')
        super(SocialStreamPostBIT, (self - bit_posts))._compute_post_link()

        for post in bit_posts:
            post.post_link = False

    def get_bit_comments(self, page=1):
        comments = [] 
        for m in self.post_id.comments_ids:
            comments.append({
                "id":m.id,
                "message":m.comment,
                "from":{
                    "id":m.partner_id.id,
                    "name":m.partner_id.name,
                    "profile_image_url_https":"https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png"
                },
                "created_time":self.env['social.stream.post']._format_published_date(m.create_date),
                "formatted_created_time":m.create_date.strftime('%m/%d/%Y'),
                "user_likes":True,
                "likes":{
                    "summary":{
                        "total_count":0
                    }
                }
            })
        return {
            'comments': list(reversed(comments))
        }

    def _compute_stream_post_image_urls(self):
        """ See field 'help' for more information. """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for stream_post in self:
            if stream_post.media_type == 'bit':
                stream_post.stream_post_image_urls = json.dumps([{'url':url_join(base_url,'web/image/%s' % image_id.id), 'mimetype':True if image_id.mimetype.startswith('image') else False,'o_mimetype':image_id.mimetype,'fullpath':image_id._full_path(image_id.store_fname)} for image_id in stream_post.post_id.image_ids])
            else:
                super(SocialStreamPostBIT,self)._compute_stream_post_image_urls()