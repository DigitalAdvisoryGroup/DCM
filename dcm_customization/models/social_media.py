# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import requests

from odoo import _, models, fields
from odoo.exceptions import UserError
from werkzeug.urls import url_encode, url_join


class SocialMediaBIT(models.Model):
    _inherit = 'social.media'

    media_type = fields.Selection(selection_add=[('bit', 'BIT')])