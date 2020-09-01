# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import dateutil.parser
import requests

from odoo import models, fields, api
from werkzeug.urls import url_join
import json


class SocialStreamBIT(models.Model):
    _inherit = 'social.stream'


    def _fetch_stream_data(self):
        if self.media_id.media_type != 'bit':
            return super(SocialStreamBIT, self)._fetch_stream_data()
        return self._fetch_bit_posts()

    def _fetch_bit_posts(self):
        self.ensure_one()
        account_id = self.env.ref("dcm_customization.social_account_bit")
        stream_posts = self.env['social.post'].sudo().search([('account_ids','in',account_id.ids),('state','=','posted')])
        posts_to_create = []
        for post in stream_posts:
            image_urls = []
            for i in post.image_ids:
                image_urls.append((0,0,{'image_url':'web/image/%s'%i.id}))
            values = {
                'stream_id': self.id,
                'post_id': post.id,
                'message': post.message,
                'author_name': post.create_uid.name,
                'published_date': post.published_date,
                'create_uid':post.create_uid.id,
                'stream_post_image_ids':image_urls
            }
            social_stream_post_id = self.env["social.stream.post"].search(
                [('post_id', '=', post.id)])
            if social_stream_post_id:
                social_stream_post_id.write(values)
            else:
                posts_to_create.append(values)
        stream_posts = self.env['social.stream.post'].create(posts_to_create)
        return any(stream_posts)
