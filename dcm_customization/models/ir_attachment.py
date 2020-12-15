from odoo import api, fields, models
from PIL import Image
import logging
_logger = logging.getLogger(__name__)
import io
import base64

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    img_width = fields.Float("Image Width(px)", compute="_get_widht_height_img",store=True)
    img_height = fields.Float("Image Height(px)",compute="_get_widht_height_img",store=True)
    is_video_thumnail = fields.Boolean("Video Thumnail Image")

    @api.depends("mimetype")
    def _get_widht_height_img(self):
        for att in self:
            if "image" in att.mimetype:
                if att.store_fname:
                    image64 = base64.b64encode(open(att._full_path(att.store_fname), 'rb').read())
                    image = Image.open(io.BytesIO((base64.b64decode(image64))))
                    width, height = image.size
                    att.img_width = width
                    att.img_height = height
            else:
                att.img_width = 0.0
                att.img_height = 0.0

    @api.model
    def create(self, vals):
        if vals.get('res_model') and vals.get('res_model') == 'social.post':
            name = vals.get('name').replace(" ", "_")
            vals['name'] = name
            vals['public'] = True
        return super(IrAttachment,self).create(vals)

    