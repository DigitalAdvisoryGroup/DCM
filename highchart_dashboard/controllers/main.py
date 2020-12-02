# -*- coding: utf-8 -*-

import io
import json

from odoo import http
from odoo.http import content_disposition, request


class HighchartDashboard(http.Controller):

    @http.route('/highchart_dashboard/export_dashboard', type='http', auth="user", website=True, csrf=False)
    def export_highchart_dashboard(self, dids, **kwargs):
        dashboard_ids = request.env['highchart.dashboard'].browse(eval(dids))
        header = "HighchartDashboard.json"
        dashboard_data = dashboard_ids.export_dashboards()
        return request.make_response(self.file_data(dashboard_data),
                                     headers=[('Content-Disposition', content_disposition(header)),
                                              ('Content-Type', 'text/csv;charset=utf8')])

    def file_data(self, dashboard_data):
        fp = io.StringIO()
        fp.write(json.dumps(dashboard_data))
        return fp.getvalue()
