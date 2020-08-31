# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import json
import requests

from odoo import models, fields
from werkzeug.urls import url_join


class SocialLivePostBIT(models.Model):
    _inherit = 'social.live.post'

    is_bit_post = fields.Boolean("BIT Post")

    def _refresh_statistics(self):
        super(SocialLivePostBIT, self)._refresh_statistics()
        accounts = self.env['social.account'].search([('media_type', '=', 'bit')])
        for account in accounts:
            existing_live_posts = self.sudo().search([('is_bit_post','=',True)])
            for post in existing_live_posts:
                likes_count = len(post.post_id.like_partner_ids)
                shares_count = len(post.post_id.share_ids)
                comments_count = len(post.post_id.comments_ids)
                post.write({
                    'engagement': likes_count + shares_count + comments_count,
                })


    def _post(self):
        bit_live_posts = self.filtered(lambda post: post.account_id.media_type == 'bit')
        super(SocialLivePostBIT, (self - bit_live_posts))._post()

        bit_live_posts._post_bit()

    def _post_bit(self):
        for live_post in self:
            values = {
                'state': 'posted',
                'failure_reason': False,
                'is_bit_post': True
            }
            live_post.write(values)
