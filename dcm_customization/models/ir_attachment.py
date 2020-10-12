from odoo import api, fields, models
from werkzeug.urls import url_join
import urllib.request
from PIL import Image
import logging
_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    img_width = fields.Float("Image Width(px)", compute="_get_widht_height_img")
    img_height = fields.Float("Image Height(px)",compute="_get_widht_height_img")


    @api.depends("mimetype")
    def _get_widht_height_img(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
        for att in self:
            if "image" in att.mimetype:
                url = url_join(base_url,
                               '/web/content/%s/%s' % (att.id, att.name))
                _logger.info("-----url----------------%s", url)
                image = Image.open(urllib.request.urlopen(url))
                width, height = image.size
                _logger.info("----width--------%s",width)
                _logger.info("----height-----%s", height)
                att.img_width = width
                att.img_height = height
            else:
                att.img_width = 0.0
                att.img_height = 0.0



    @api.model
    def create(self, vals):
        print("---------attachment---------------")
        if vals.get('res_model') and vals.get('res_model') == 'social.post':
            name = vals.get('name').replace(" ", "_")
            vals['name'] = name
            vals['public'] = True
        res = super(IrAttachment,self).create(vals)
        # if vals.get('res_model') == 'social.post' and "image" in res.mimetype:
        #     print("------res---------------",res)
        #     base_url = self.env['ir.config_parameter'].sudo().get_param(
        #         'web.base.url')
        #     url = url_join(base_url, '/web/content/%s/%s' % (res.id, res.name))
        #     print("-----url----------------", url)
        #     image = Image.open(urllib.request.urlopen(url))
        #     width, height = image.size
        #     print("----width--------", width)
        #     print("----height--------", height)
        #     res.write({})
        return res

    