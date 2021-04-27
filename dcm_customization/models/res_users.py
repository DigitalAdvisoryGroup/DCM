# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _login(cls, db, login, password):
        try:
            return super(ResUsers, cls)._login(db, login, password)
        except Exception as e:
            return 0

    def get_privacy_policy_url(self):
        return {'privacy_policy_url':self.company_id.privacy_policy_url or ""}

    def get_global_search_right(self, test=False):
        return self.env.user.has_group('dcm_customization.group_global_search_administrator')