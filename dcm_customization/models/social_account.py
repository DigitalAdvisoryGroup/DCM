# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SocialAccountBIT(models.Model):
    _inherit = 'social.account'

    def _compute_stats_link(self):
        bit_accounts = self.filtered(lambda account: account.media_type == 'bit')
        super(SocialAccountBIT,(self - bit_accounts))._compute_stats_link()
        for account in bit_accounts:
            account.stats_link = "https://www.candidroot.com"

    
    def _compute_statistics(self):
        bit_accounts = self.filtered(lambda account: account.media_type == 'bit')
        super(SocialAccountBIT, (self - bit_accounts))._compute_statistics()
        for account in bit_accounts:
            account_stats = account._get_bit_account_stats()
            account.write({
                'audience': account_stats.get('share_count'),
                'engagement': account_stats.get('like_count'),
                'stories': account_stats.get('comments_count'),
            })

    def _get_bit_account_stats(self):
        """ Query the account information to retrieve the Twitter audience (= followers count). """
        likes = self.env['social.post'].search([('account_ids','in',self.id)])
        like_count = 0
        comments_count = 0
        share_count = 0
        for l in likes:
            like_count += l.engagement
            comments_count += len(l.comments_ids.ids)
            share_count += len(l.share_ids.ids)
        return {

            'like_count':like_count,
            'comments_count':comments_count,
            'share_count':share_count
        }


    @api.model
    def refresh_statistics(self):
        """ Will re-compute the statistics of all active accounts. """
        res = super(SocialAccountBIT,self).refresh_statistics()
        account_id = self.env.ref("dcm_customization.social_media_bit").id
        for record in res:
            record['is_bit_account'] = False
            if record['media_id'][0] == account_id:
                record['is_bit_account'] = True
        return res