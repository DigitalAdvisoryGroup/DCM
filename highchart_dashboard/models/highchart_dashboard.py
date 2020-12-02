# -*- coding: utf-8 -*-

import json

from odoo import models, fields, api, _


class HighchartDashboard(models.Model):
    _name = 'highchart.dashboard'

    name = fields.Char('Name', required=True)
    menu_sequence = fields.Integer('Menu Sequence', default=10)
    chart_ids = fields.One2many('highchart.dashboard.chart', 'dashboard_id', 'Dashboard Chats')
    charts_count = fields.Integer('Charts Count', compute='_compute_chart_count')

    menu_id = fields.Many2one('ir.ui.menu')
    menu_name = fields.Char('Menu Name', required=True)
    parent_menu_id = fields.Many2one('ir.ui.menu', 'Parent Menu', required=True)

    active = fields.Boolean("Active", default=True)
    group_ids = fields.Many2many('res.groups', string='Group Access')
    client_action_id = fields.Many2one('ir.actions.client')

    refresh_interval = fields.Selection([
        ('15000', '15 Seconds'),
        ('30000', '30 Seconds'),
        ('45000', '45 Seconds'),
        ('60000', '1 minute'),
        ('120000', '2 minute'),
        ('300000', '5 minute'),
        ('600000', '10 minute'),
    ], string="Refresh Interval")

    @api.depends('chart_ids')
    def _compute_chart_count(self):
        for dashboard in self:
            dashboard.charts_count = self.env['highchart.dashboard.chart'].search_count(
                [('dashboard_id', '=', dashboard.id)])

    def button_dashboard_charts(self):
        for dashboard in self:
            charts = self.env['highchart.dashboard.chart'].search([('dashboard_id', '=', dashboard.id)])
            views = [
                [self.env.ref('highchart_dashboard.view_highchart_dashboard_chart_tree').id, 'tree'],
                [self.env.ref('highchart_dashboard.view_highchart_dashboard_chart_form').id, 'form']
            ]
            action = {
                'name': _('Charts'),
                'type': 'ir.actions.act_window',
                'res_model': 'highchart.dashboard.chart',
                'view_type': 'form',
                'view_mode': 'tree, form',
                'views': views,
                'domain': [["id", "in", charts.ids]],
                'context': {'default_dashboard_id': dashboard.id}
            }
            if len(charts) == 1:
                action['views'] = [[self.env.ref('highchart_dashboard.view_highchart_dashboard_chart_form').id, 'form']]
                action['res_id'] = charts.id
            return action

    @api.model
    def create(self, vals):
        res = super(HighchartDashboard, self).create(vals)
        if res.menu_name and res.parent_menu_id:
            client_action_id = self.env['ir.actions.client'].sudo().create({
                'params': {'dashboard_id': res.id},
                'name': res.name,
                'res_model': 'highchart.dashboard',
                'tag': 'highchart_main_dashboard',
            })
            menu_id = self.env['ir.ui.menu'].sudo().create({
                'name': res.menu_name,
                'parent_id': res.parent_menu_id.id,
                'sequence': res.menu_sequence,
                'action': "ir.actions.client," + str(client_action_id.id),
                'groups_id': [(6, 0, res.group_ids.ids)]
            })
            res.client_action_id = client_action_id
            res.menu_id = menu_id
        return res

    def write(self, vals):
        res = super(HighchartDashboard, self).write(vals)
        for dashboard in self:
            if 'menu_name' in vals:
                dashboard.menu_id.sudo().name = vals['menu_name']
            if 'name' in vals:
                dashboard.client_action_id.sudo().name = vals['name']
            if 'menu_sequence' in vals:
                dashboard.menu_id.sudo().sequence = vals['menu_sequence']
            if 'parent_menu_id' in vals:
                dashboard.menu_id.sudo().parent_id = vals['parent_menu_id']
            if 'group_ids' in vals:
                dashboard.menu_id.sudo().groups_id = vals['group_ids']
            if 'active' in vals:
                dashboard.menu_id.sudo().active = vals['active']
        return res

    def unlink(self):
        for rec in self:
            rec.client_action_id.unlink()
            rec.menu_id.unlink()
        return super(HighchartDashboard, self).unlink()

    @api.model
    def get_dashboard_data(self, client_action_id, date_filter_type='none', custom_start_date=False, custom_end_date=False):
        dashboard = self.search([('client_action_id', '=', client_action_id)])
        all_dashboard_ids = self.env['highchart.dashboard'].search([])
        all_dashboards = [{'id': x.id, 'name': x.name} for x in all_dashboard_ids]
        dashboard_data = {'dashboard_id': dashboard.id, 'dashboard_name': dashboard.name,
                          'refresh_interval': dashboard.refresh_interval, 'all_dashboards': all_dashboards,
                          'dashboard_charts': []}

        dashboard_charts = []
        for chart in dashboard.chart_ids:
            if chart.active:
                if chart.gs_height:
                    gs_height = chart.gs_height
                else:
                    gs_height = chart.chart_type == 'tile' and 2 or 3

                ctx = self._context.copy()
                ctx.update({'lang': self.env.user.lang,
                            'date_filter_type': date_filter_type,
                            'custom_start_date': custom_start_date,
                            'custom_end_date': custom_end_date})
                chart = chart.with_context(ctx)

                dashboard_charts.append({
                    'chart_id': chart.id,
                    'name': chart.name,
                    'chart_type': chart.chart_type,
                    'model_name': chart.model_name,
                    'domain': chart.all_domain,
                    'group_by': chart.chart_groupby_type in ['relational_type', 'date_type'] and (
                        chart.chart_groupby_type == 'relational_type' and chart.chart_groupby_id.name or
                        chart.chart_groupby_id.name + ':' + chart.chart_groupby_date) or False,
                    'tile_template': chart.tile_template,
                    'icon_option': chart.icon_option,
                    'upload_icon_binary': chart.upload_icon_binary,
                    'default_icon': chart.default_icon,
                    'icon_color': chart.icon_color,
                    'font_color': chart.font_color,
                    'background_color': chart.background_color,
                    'total_record': chart.total_record,
                    'gs_x': chart.gs_x,
                    'gs_y': chart.gs_y,
                    'data_gs_height': gs_height,
                    'data_gs_min_height': chart.chart_type in ['tile', 'kpi'] and 2 or 4,
                    'data_gs_width': chart.gs_width and chart.gs_width or (
                        chart.chart_type in ['tile', 'kpi'] and 3 or 4),
                    'data_gs_min_width': chart.chart_type in ['tile', 'kpi'] and 3 or 4,
                    'data_gs_auto_position': True if (chart.gs_x == 0 and chart.gs_y == 0) else False,
                    'gs_height': chart.gs_height,
                    'gs_width': chart.gs_width,
                    'second_model_id': chart.second_model_id.id,
                    'kpi_target': chart.kpi_target,
                    'kpi_value': chart.kpi_value,
                    'target_display_value': chart.target_display_value,
                    'data_comparision': chart.data_comparision,
                    'target_value_type': chart.target_value_type,
                    'kpi_target_view_type': chart.kpi_target_view_type,
                    'progress_bar_value': chart.progress_bar_value,
                    'progress_bar_max': chart.progress_bar_max,
                    'chart_data': chart.chart_data,
                    'list_view_ref': chart.list_view_ref_id and chart.list_view_ref_id.id or False,
                    'form_view_ref': chart.form_view_ref_id and chart.form_view_ref_id.id or False
                })
        dashboard_data['dashboard_charts'] = dashboard_charts

        return json.dumps(dashboard_data)

    @api.model
    def write_dashboard_data(self, dashboard_id, size_and_move_changes):
        for k, v in size_and_move_changes.items():
            chart = self.env['highchart.dashboard.chart'].browse(int(k))
            chart.write(v)

    def export_dashboards(self):
        all_dashboard = []
        for dashboard in self:
            dashboard_data = {
                'name': dashboard.name,
                'menu_name': dashboard.menu_name,
                'parent_menu_name': dashboard.parent_menu_id.name,
                'menu_sequence': dashboard.menu_sequence,
                'refresh_interval': dashboard.refresh_interval,
                'charts_data': []
            }

            for chart in dashboard.chart_ids:
                chart_data = {
                    'name': chart.name,
                    'model_name': chart.model_name,
                    'domain': chart.domain,

                    'chart_type': chart.chart_type,
                    'filter_date_field': chart.filter_date_field.name,
                    'chart_date_filter': chart.chart_date_filter,
                    'calculation_type': chart.calculation_type,
                    'record_field': chart.record_field.name,
                    'sort_by': chart.sort_by.name,
                    'order_by': chart.order_by,
                    'record_limit': chart.record_limit,
                    'chart_groupby_id': chart.chart_groupby_id.name,
                    'chart_groupby_date': chart.chart_groupby_date,
                    'chart_measure_field_ids': [x.name for x in chart.chart_measure_field_ids],
                    'list_view_type': chart.list_view_type,
                    'list_view_fields': [x.name for x in chart.list_view_fields],
                    'list_view_group_fields': [x.name for x in chart.list_view_group_fields],

                    'tile_template': chart.tile_template,
                    'icon_option': chart.icon_option,
                    'default_icon': chart.default_icon,
                    'font_color': chart.font_color,
                    'background_color': chart.background_color,
                    'icon_color': chart.icon_color,

                    'second_model_name': chart.second_model_name,
                    'second_calculation_type': chart.second_calculation_type,
                    'second_record_field': chart.second_record_field.name,
                    'data_comparision': chart.data_comparision,
                    'second_domain': chart.second_domain,
                    'second_filter_date_field': chart.second_filter_date_field.name,
                    'second_date_filter': chart.second_date_filter,
                    'kpi_target': chart.kpi_target,
                    'kpi_target_value': chart.kpi_target_value,
                    'kpi_target_view_type': chart.kpi_target_view_type,

                    'gs_x': chart.gs_x,
                    'gs_y': chart.gs_y,
                    'gs_width': chart.gs_width,
                    'gs_height': chart.gs_height,
                }

                dashboard_data['charts_data'].append(chart_data)
            all_dashboard.append(dashboard_data)
        return all_dashboard
