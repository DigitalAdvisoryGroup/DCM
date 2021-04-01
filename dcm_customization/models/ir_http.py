# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.http import request, content_disposition
import base64
import re

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='name', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None):
        status, headers, content = super(Http, self).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype=default_mimetype, access_token=access_token)
        file_len = len(base64.b64decode(content))
        response_length = file_len
        if request.httprequest.environ.get('HTTP_RANGE', False):
            try:
                first, last = parse_byte_range(request.httprequest.environ.get('HTTP_RANGE'))
            except ValueError as e:
                return 400, [], None
            # Fix last for "x-" like ranges
            if last is None or last >= file_len:
                last = file_len - 1
            if first >= file_len:
                return 416, [], None
            status = 206
            # Offset ranges needs offset content
            if first != 0:
                if last != file_len - 1:
                    couple_bytes = base64.b64decode(content)[first:last]
                else:
                    couple_bytes = base64.b64decode(content)[first:]
                content = base64.b64encode(couple_bytes)
            response_length = last - first + 1
            headers.append(('Content-Range', 'bytes %s-%s/%s' % (first, last, file_len)))
            headers.append(('Accept-Ranges', 'bytes'))
        headers.append(('Content-Length', str(response_length)))
        return status, headers, content

BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')


def parse_byte_range(byte_range):
    """Returns the two numbers in 'bytes=123-456' or throws ValueError.
    The last number or both numbers may be None.
    """
    if byte_range.strip() == '':
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError('Invalid byte range %s' % byte_range)

    first, last = [x and int(x) for x in m.groups()]
    if last and last < first:
        raise ValueError('Invalid byte range %s' % byte_range)
    return first, last

