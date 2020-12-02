# -*- coding: utf-8 -*-

import base64
import json
import os

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ImportDashboardWizard(models.TransientModel):
    _name = "import.dashboard.wizard"

    file = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')

    @api.model
    def json_validator(self, xml_name):
        name, extension = os.path.splitext(xml_name)
        return True if extension == '.json' else False

    def import_button(self):
        if not self.json_validator(self.file_name):
            raise UserError(_("The file must be extension .json"))

        try:
            all_dashboards = json.loads(base64.b64decode(self.file))
        except Exception as e:
            raise ValidationError(_("This file is not supported"))

        for dashboard in all_dashboards:
            new_dashboard = self.env['highchart.dashboard'].create(
                {'name': dashboard['name'], 'menu_name': dashboard['menu_name'],
                 'menu_sequence': dashboard['menu_sequence'], 'refresh_interval': dashboard['refresh_interval'],
                 'parent_menu_id': self.env.ref('highchart_dashboard.highchart_dashboards_root_menu').id})
            chart_ids = []
            for chart in dashboard['charts_data']:
                chart_data = chart.copy()
                model_id = self.env['ir.model'].search([('model', '=', chart['model_name'])])
                if model_id:
                    chart_data['model_id'] = model_id.id
                    if chart.get('chart_groupby_id', False):
                        chart_groupby_id = self.env['ir.model.fields'].search(
                            [('name', '=', chart['chart_groupby_id']), ('model_id', '=', model_id.id)])
                        chart_data['chart_groupby_id'] = chart_groupby_id.id

                    if chart.get('record_field', False):
                        record_field = self.env['ir.model.fields'].search(
                            [('name', '=', chart['record_field']), ('model_id', '=', model_id.id)])
                        chart_data['record_field'] = record_field.id

                    if chart.get('filter_date_field', False):
                        filter_date_field = self.env['ir.model.fields'].search(
                            [('name', '=', chart['filter_date_field']), ('model_id', '=', model_id.id)])
                        chart_data['filter_date_field'] = filter_date_field.id

                    if chart.get('sort_by', False):
                        sort_by = self.env['ir.model.fields'].search(
                            [('name', '=', chart['sort_by']), ('model_id', '=', model_id.id)])
                        chart_data['sort_by'] = sort_by.id

                    if chart.get('chart_measure_field_ids', False):
                        chart_measure_field_ids = self.env['ir.model.fields']
                        for f in chart['chart_measure_field_ids']:
                            temp = self.env['ir.model.fields'].search(
                                [('name', '=', f), ('model_id', '=', model_id.id)])
                            if temp:
                                chart_measure_field_ids |= temp
                        chart_data['chart_measure_field_ids'] = chart_measure_field_ids

                    if chart.get('list_view_fields', False):
                        list_view_fields = self.env['ir.model.fields']
                        for f in chart['list_view_fields']:
                            temp = self.env['ir.model.fields'].search(
                                [('name', '=', f), ('model_id', '=', model_id.id)])
                            if temp:
                                list_view_fields |= temp
                        chart_data['list_view_fields'] = list_view_fields

                    if chart.get('list_view_group_fields', False):
                        list_view_group_fields = self.env['ir.model.fields']
                        for f in chart['list_view_group_fields']:
                            temp = self.env['ir.model.fields'].search(
                                [('name', '=', f), ('model_id', '=', model_id.id)])
                            if temp:
                                list_view_group_fields |= temp
                        chart_data['list_view_group_fields'] = list_view_group_fields

                    if chart.get('second_model_name', False):
                        second_model_id = self.env['ir.model'].search([('model', '=', chart['second_model_name'])])
                        if second_model_id:
                            chart_data['second_model_id'] = second_model_id.id

                            if chart.get('second_record_field', False):
                                second_record_field = self.env['ir.model.fields'].search(
                                    [('name', '=', chart['second_record_field']), ('model_id', '=', second_model_id.id)])
                                chart_data['second_record_field'] = second_record_field.id

                            if chart.get('second_filter_date_field', False):
                                second_filter_date_field = self.env['ir.model.fields'].search(
                                    [('name', '=', chart['second_filter_date_field']), ('model_id', '=', second_model_id.id)])
                                chart_data['second_filter_date_field'] = second_filter_date_field.id

                chart_ids.append(chart_data)
            new_dashboard.chart_ids = [(0, 0, chart_dict) for chart_dict in chart_ids]
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
