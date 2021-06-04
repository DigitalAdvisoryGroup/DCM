from odoo import api, models, fields, _, tools
import logging
_logger = logging.getLogger(__name__)


class APIData(models.Model):
    _name = 'api.data'
    _description = 'API Data'
    # _rec_name = "partner_id"

