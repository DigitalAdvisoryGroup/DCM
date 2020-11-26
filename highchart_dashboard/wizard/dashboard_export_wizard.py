# -*- coding: utf-8 -*-

from odoo import models, api


class DashboardExportWizard(models.TransientModel):
    _name = "dashboard.export.wizard"
    _description = "dashboard.export.wizard"

    def download_file(self):
        dashboard_ids = self.env['highchart.dashboard'].browse(self.env.context.get('active_ids', False))
        return {
            'type': 'ir.actions.act_url',
            'url': '/highchart_dashboard/export_dashboard?dids=%s' % str(dashboard_ids.ids),
            'target': 'self',
        }
