# -*- coding: utf-8 -*-
from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_global_search_right(self, test=False):
        return self.env.user.has_group('global_search_cr.group_global_search_administrator')
