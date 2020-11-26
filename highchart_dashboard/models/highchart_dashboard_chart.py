# -*- coding: utf-8 -*-

import json
import math

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
import calendar


DATE_FILTER_OPTIONS = [
    ('none', 'None'),
    ('today', 'Today'),
    ('this_week', 'This Week'),
    ('this_month', 'This Month'),
    ('this_quarter', 'This Quarter'),
    ('this_year', 'This Year'),
    ('next_day', 'Next Day'),
    ('next_week', 'Next Week'),
    ('next_month', 'Next Month'),
    ('next_quarter', 'Next Quarter'),
    ('next_year', 'Next Year'),
    ('last_day', 'Last Day'),
    ('last_week', 'Last Week'),
    ('last_month', 'Last Month'),
    ('last_quarter', 'Last Quarter'),
    ('last_year', 'Last Year'),
    ('last_7_days', 'Last 7 Days'),
    ('last_30_days', 'Last 30 Days'),
    ('last_90_days', 'Last 90 Days'),
    ('last_365_days', 'Last 365 Days'),
    ('custom', 'Custom Filter'),
]


def calculate_aspect(w, h):
    def gcd(a, b):
        return a if b == 0 else gcd(b, a % b)

    r = gcd(w, h)
    x = int(w / r)
    y = int(h / r)
    return str(round(x / y, 2)) + ':' + str(round(y / y, 2))


class HighchartDashboardChart(models.Model):
    _name = 'highchart.dashboard.chart'
    _description = 'highchart.dashboard.chart'

    name = fields.Char('Name', required=True)
    dashboard_id = fields.Many2one('highchart.dashboard', 'Dashboard', required=True, ondelete='cascade')

    model_id = fields.Many2one('ir.model', 'Model', required=True,
                               domain="[('access_ids','!=',False),('transient','=',False),('model','not ilike','base_import%'),('model','not ilike','ir.%'),('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),('model','!=','mail.thread'),('model','!=','highchart.dashboard'),('model','!=','highchart.dashboard.chart')]")
    model_name = fields.Char(related='model_id.model')
    domain = fields.Char("Domain")
    all_domain = fields.Char('All Domain', compute='_compute_all_domain')
    domain_temp = fields.Char(string="Domain Substitute")
    filter_date_field = fields.Many2one('ir.model.fields', 'Filter Date Field',
                                        domain="[('model_id', '=', model_id), '|', ('ttype','=','date'), ('ttype','=','datetime')]")
    list_view_ref_id = fields.Many2one('ir.ui.view', 'List View Ref', domain="[('model', '=', model_name), ('type', '=', 'tree')]")
    form_view_ref_id = fields.Many2one('ir.ui.view', 'Form View Ref', domain="[('model', '=', model_name), ('type', '=', 'form')]")

    chart_date_filter = fields.Selection(DATE_FILTER_OPTIONS, 'Chart Date Filter', default='none')

    chart_type = fields.Selection([
        ('tile', 'Tile'),
        ('column', 'Bar Chart'),
        ('bar', 'Horizontal Bar Chart'),
        ('line', 'Line Chart'),
        ('area', 'Area Chart'),
        ('pie', 'Pie Chart'),
        ('polar', 'Polar Area Chart'),
        ('list_view', 'List View'),
        ('kpi', 'KPI')], "Chart Type", default=lambda self: self._context.get('chart_type', 'tile'), required=True)

    calculation_type = fields.Selection([
        ('count', 'Count'), ('sum', 'Sum'), ('average', 'Average')], "Calculation Type", default="count")

    record_field = fields.Many2one('ir.model.fields', 'Record Field',
                                   domain="[('model_id','=', model_id),('name','!=','id'),"
                                          "'|','|',('ttype','=','integer'),('ttype','=','float'),"
                                          "('ttype','=','monetary')]")

    font_color = fields.Char('Font Color', default="#FFFFFF")
    background_color = fields.Char('Background Color', default="#00BD00")
    icon_color = fields.Char('Icon Color', default="#000000")

    icon_option = fields.Selection([('default', 'Default'), ('upload', 'Upload')], "Icon Option", default="default")
    default_icon = fields.Char("Default Icon", default="fa fa-book")
    upload_icon = fields.Binary("Upload Icon")
    upload_icon_binary = fields.Char('Upload Icon Binary', compute="_compute_get_icon_binary", store=True)

    record_limit = fields.Integer("Record Limit")
    order_by = fields.Selection([('ASC', 'Ascending'), ('DESC', 'Descending')], "Order By", default='ASC')
    sort_by = fields.Many2one('ir.model.fields', "Sort By",
                              domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),('ttype','!=','one2many'),('ttype','!=','many2one'),('ttype','!=','binary')]")

    chart_measure_field_ids = fields.Many2many('ir.model.fields', 'measure_field_rel', 'measure_field_id', 'field_id',
                                               string="Measure Fields",
                                               domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),'|','|',('ttype','=','integer'),('ttype','=','float'),('ttype','=','monetary')]")
    chart_groupby_id = fields.Many2one('ir.model.fields', "Group By",
                                       domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),('ttype','in',['many2one', 'date', 'datetime', 'char', 'float', 'selection', 'boolean', 'text', 'monetary', 'integer'])]")

    chart_groupby_date = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year')], "Group By Date Type", default='day')

    chart_sub_groupby_id = fields.Many2one('ir.model.fields', "Sub Group By",
                                           domain="[('model_id','=',model_id),('name','!=','id'),('store','=',True),('ttype','in',['many2one', 'date', 'datetime', 'char', 'float', 'selection', 'boolean', 'text', 'monetary', 'integer'])]")

    chart_sub_groupby_date = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year')], "Group By Date Type", default='day')

    tile_template = fields.Selection([
        ('template1', 'Template 1'),
        ('template2', 'Template 2'),
        ('template3', 'Template 3'),
        ('template4', 'Template 4'),
        ('template5', 'Template 5'),
        ('template6', 'Template 6')], "Template", default='template1')

    list_view_type = fields.Selection([('ungrouped', 'Un-Grouped'), ('grouped', 'Grouped')], "List View Type",
                                      default="ungrouped")
    list_view_fields = fields.Many2many('ir.model.fields', 'chart_list_field_rel', 'chart_id', 'field_id',
                                        string="List View Fields",
                                        domain="[('model_id','=',model_id), ('store','=',True), ('ttype','!=','one2many'),('ttype','!=','many2many'),('ttype','!=','binary')]")

    list_view_group_fields = fields.Many2many('ir.model.fields', 'chart_list_groupby_field_rel', 'chart_id', 'field_id',
                                              string="List View Group By Fields",
                                              domain="[('model_id','=',model_id), ('name','!=','id'), ('store','=',True), '|', '|', ('ttype','=','integer'),('ttype','=','float'), ('ttype','=','monetary')]")

    active = fields.Boolean("Active", default=True)
    gs_x = fields.Integer('GS-X', default=0)
    gs_y = fields.Integer('GS-Y', default=0)
    gs_width = fields.Integer('GS-width', default=0)
    gs_height = fields.Integer('GS-height', default=0)

    chart_preview = fields.Char('Preview')
    chart_groupby_type = fields.Char(compute='_compute_chart_groupby_type')
    chart_sub_groupby_type = fields.Char(compute='_compute_chart_sub_groupby_type')
    total_record = fields.Integer(string="Record Count", compute='_compute_total_record', digits=(16, 2))
    chart_data = fields.Char("Chart Data", compute='_compute_chart_data',compute_sudo=True)

    second_model_id = fields.Many2one('ir.model', 'Model',
                                      domain="[('access_ids','!=',False),('transient','=',False),('model','not ilike','base_import%'),('model','not ilike','ir.%'),('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),('model','!=','mail.thread'),('model','!=','highchart.dashboard'),('model','!=','highchart.dashboard.chart')]")
    second_model_name = fields.Char(related='second_model_id.model')
    second_calculation_type = fields.Selection([('count', 'Count'), ('sum', 'Sum'), ('average', 'Average')],
                                               "Calculation Type", default="count")
    second_record_field = fields.Many2one('ir.model.fields', 'Record Field',
                                          domain="[('model_id','=', second_model_id),('name','!=','id'), '|', '|', ('ttype','=','integer'),('ttype','=','float'), ('ttype','=','monetary')]")
    second_total_record = fields.Integer("Record Count", compute='_compute_second_total_record', digits=(16, 2))
    kpi_value = fields.Char("KPI Value", compute='_compute_second_total_record')
    data_comparision = fields.Selection(
        [('none', 'None'), ('sum', 'Sum'), ('ratio', 'Ratio'), ('percentage', 'Percentage')], "Comparision",
        default="none")
    second_domain = fields.Char("Domain")
    second_filter_date_field = fields.Many2one('ir.model.fields', 'Filter Date Field',
                                               domain="[('model_id', '=', second_model_id), '|', ('ttype','=','date'), ('ttype','=','datetime')]")
    second_date_filter = fields.Selection(DATE_FILTER_OPTIONS, 'Chart Date Filter', default='none')

    kpi_target = fields.Boolean('Is Target ?')
    kpi_target_value = fields.Float('Target', digits=(16, 2))
    kpi_target_view_type = fields.Selection([('number', 'Number'), ('progress_bar', 'Progress Bar')],
                                            'Target View Type', default='number')
    target_display_value = fields.Char('Target Display Value', compute='_compute_second_total_record')
    target_value_type = fields.Char('Target Value Type', compute='_compute_second_total_record')
    progress_bar_value = fields.Char('Progress Bar Value', compute='_compute_second_total_record')
    progress_bar_max = fields.Char('Progress Bar Value', compute='_compute_second_total_record')
    chart_theme = fields.Selection([('default', 'Default'), ('light', 'Light'), ('dark', 'Dark'), ('multi', 'Multi')],
                                   string="Chart Theme", default='default')
    stack_options = fields.Boolean('Stack Options')
    show_unit = fields.Boolean('Show Data Value', default=True)
    show_custom_unit = fields.Boolean('Show Custom Unit', default=False)
    select_unit_type = fields.Selection([('monetary', 'Monetary'), ('custom', 'Custom')], "Select Unit Type", default='monetary')
    custom_unit = fields.Char('Custom Unit')
    show_legend = fields.Boolean('Show lagend', default=True)

    @api.depends('domain', 'filter_date_field', 'chart_date_filter')
    def _compute_all_domain(self):
        for chart in self:
            chart.all_domain = chart.generate_domain()

    def generate_domain(self):
        for chart in self:
            model_domain = date_filter = []
            ctx = self._context.copy()
            if chart.filter_date_field and chart.chart_date_filter == 'none' and ctx.get('date_filter_type', False) and ctx['date_filter_type'] != 'none':
                if ctx['date_filter_type'] == 'custom' and ctx.get('custom_start_date', False) and ctx.get('custom_end_date', False):
                    start_date = datetime.strptime(ctx['custom_start_date'], '%m/%d/%Y').replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = datetime.strptime(ctx['custom_end_date'], '%m/%d/%Y').replace(hour=23, minute=59, second=59, microsecond=0)
                    date_filter = [(chart.filter_date_field.name, ">=", fields.Datetime.to_string(start_date)),
                                   (chart.filter_date_field.name, "<=", fields.Datetime.to_string(end_date))]
                else:
                    filter_dates = chart.get_filter_start_and_end_date(ctx['date_filter_type'])
                    start_date = filter_dates[0]
                    end_date = filter_dates[1]
                    date_filter = [(chart.filter_date_field.name, ">=", fields.Datetime.to_string(start_date)),
                                   (chart.filter_date_field.name, "<=", fields.Datetime.to_string(end_date))]
            elif chart.filter_date_field and chart.chart_date_filter != 'none':
                filter_dates = chart.get_filter_start_and_end_date(chart.chart_date_filter)
                start_date = filter_dates[0]
                end_date = filter_dates[1]
                date_filter = [(chart.filter_date_field.name, ">=", fields.Datetime.to_string(start_date)),
                               (chart.filter_date_field.name, "<=", fields.Datetime.to_string(end_date))]

            if chart.domain and "%UID" in chart.domain:
                model_domain = eval(chart.domain.replace('"%UID"', str(self.env.user.id)))
            elif chart.domain:
                model_domain = eval(chart.domain)
            return str(model_domain + date_filter)

    @api.depends('calculation_type', 'model_id', 'domain', 'record_field', 'chart_date_filter')
    def _compute_total_record(self):
        for chart in self:
            ctx = self._context.copy()
            if chart.filter_date_field and chart.chart_date_filter == 'none' and ctx.get('date_filter_type', False):
                domain = eval(chart.generate_domain())
            else:
                domain = eval(chart.all_domain)

            if chart.calculation_type == 'count' and chart.model_id:
                chart.total_record = self.env[chart.model_id.model].search_count(domain)
            elif chart.calculation_type == 'sum' and chart.model_id and chart.record_field:
                records = self.env[chart.model_id.model].search(domain)
                chart.total_record = sum([x[chart.record_field.name] for x in records])
            elif chart.calculation_type == 'average' and chart.model_id and chart.record_field:
                total_record = self.env[chart.model_id.model].search_count(domain)
                records = self.env[chart.model_id.model].search(domain)
                total_sum = sum([x[chart.record_field.name] for x in records])
                if total_sum > 0:
                    chart.total_record = total_sum / total_record
                else:
                    chart.total_record = 0
            else:
                chart.total_record = 0

    def get_filter_start_and_end_date(self, date_filter_type='none'):
        start_date = datetime.now()
        end_date = datetime.now()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if date_filter_type == 'none':
            start_date = datetime.now()
            end_date = datetime.now()
        elif date_filter_type == 'today':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'this_week':
            start_date = today - timedelta(days=today.weekday())
            end_date = ((today - timedelta(days=today.weekday())) + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'this_month':
            start_date = today.replace(day=1)
            month = calendar.monthrange(datetime.now().year,datetime.now().month)
            end_date = datetime.now().replace(day=month[1]).replace(hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'this_quarter':
            if math.ceil(today.month / 3.) == 1:
                start_date = today.replace(day=1, month=1)
                end_date = today.replace(day=31, month=3, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3.) == 2:
                start_date = today.replace(day=1, month=4)
                end_date = today.replace(day=30, month=6, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3.) == 3:
                start_date = today.replace(day=1, month=7)
                end_date = today.replace(day=30, month=9, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3.) == 4:
                start_date = today.replace(day=1, month=10)
                end_date = today.replace(day=31, month=12, hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'this_year':
            start_date = today.replace(day=1, month=1)
            end_date = today.replace(day=31, month=12, hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'next_day':
            start_date = today + relativedelta(days=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today + relativedelta(days=1, hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'next_week':
            start_date = (today - timedelta(days=today.weekday())) + relativedelta(days=7)
            end_date = (start_date + relativedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'next_month':
            start_date = (today + relativedelta(day=31)) + relativedelta(days=1)
            end_date = ((today + relativedelta(months=1)) + relativedelta(day=31)).replace(hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'next_quarter':
            today = today + relativedelta(months=3)
            if math.ceil(today.month / 3) == 1:
                start_date = today.replace(day=1, month=1)
                end_date = today.replace(day=31, month=3, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3) == 2:
                start_date = today.replace(day=1, month=4)
                end_date = today.replace(day=30, month=6, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3) == 3:
                start_date = today.replace(day=1, month=7)
                end_date = today.replace(day=30, month=9, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3) == 4:
                start_date = today.replace(day=1, month=10)
                end_date = today.replace(day=31, month=12, hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'next_year':
            start_date = today.replace(month=1, day=1) + relativedelta(years=1)
            end_date = today.replace(month=12, day=31) + relativedelta(years=1, hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'last_day':
            start_date = today - relativedelta(days=1)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=59)
        elif date_filter_type == 'last_week':
            today = today - relativedelta(weeks=1)
            start_date = today - timedelta(days=today.weekday())
            end_date = ((today - timedelta(days=today.weekday())) + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'last_month':
            start_date = today.replace(day=1) - relativedelta(months=1)
            end_date = (today.replace(day=1) - relativedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'last_quarter':
            today = today - relativedelta(months=3)
            if math.ceil(today.month / 3) == 1:
                start_date = today.replace(day=1, month=1)
                end_date = today.replace(day=31, month=3, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3) == 2:
                start_date = today.replace(day=1, month=4)
                end_date = today.replace(day=30, month=6, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3) == 3:
                start_date = today.replace(day=1, month=7)
                end_date = today.replace(day=30, month=9, hour=23, minute=59, second=59, microsecond=0)
            elif math.ceil(today.month / 3) == 4:
                start_date = today.replace(day=1, month=10)
                end_date = today.replace(day=31, month=12, hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'last_year':
            start_date = today.replace(month=1, day=1) - relativedelta(years=1)
            end_date = today.replace(month=12, day=31) - relativedelta(years=1, hour=23, minute=59, second=59, microsecond=0)
        elif date_filter_type == 'last_7_days':
            start_date = today - relativedelta(days=7)
        elif date_filter_type == 'last_30_days':
            start_date = today - relativedelta(days=30)
        elif date_filter_type == 'last_90_days':
            start_date = today - relativedelta(days=90)
        elif date_filter_type == 'last_365_days':
            start_date = today - relativedelta(days=365)
        return (start_date, end_date)

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.calculation_type = 'count'
        self.chart_groupby_id = False
        self.record_field = False
        self.sort_by = False
        self.chart_measure_field_ids = False
        self.domain = '[]'

    @api.onchange('second_model_id')
    def onchange_second_model_id(self):
        self.second_record_field = False
        self.second_filter_date_field = False
        self.second_date_filter = False
        self.second_domain = '[]'

    @api.onchange('kpi_target')
    def onchange_kpi_target(self):
        if not self.kpi_target:
            self.kpi_target_value = 0

    @api.depends('chart_groupby_id')
    def _compute_chart_groupby_type(self):
        for rec in self:
            if rec.chart_groupby_id.ttype == 'datetime' or rec.chart_groupby_id.ttype == 'date':
                rec.chart_groupby_type = 'date_type'
            elif rec.chart_groupby_id.ttype == 'many2one':
                rec.chart_groupby_type = 'relational_type'
            else:
                rec.chart_groupby_type = 'none'

    @api.depends('chart_sub_groupby_id')
    def _compute_chart_sub_groupby_type(self):
        for rec in self:
            if rec.chart_sub_groupby_id.ttype == 'datetime' or rec.chart_sub_groupby_id.ttype == 'date':
                rec.chart_sub_groupby_type = 'date_type'
            elif rec.chart_sub_groupby_id.ttype == 'many2one':
                rec.chart_sub_groupby_type = 'relational_type'
            else:
                rec.chart_sub_groupby_type = 'none'

    @api.depends('upload_icon')
    def _compute_get_icon_binary(self):
        for chart in self:
            if chart.upload_icon:
                chart.upload_icon_binary = chart.upload_icon

    @api.model
    @api.depends('name', 'chart_measure_field_ids', 'list_view_type', 'list_view_fields', 'list_view_group_fields',
                 'chart_groupby_id', 'domain', 'chart_type', 'chart_groupby_type', 'chart_groupby_date', 'model_id',
                 'sort_by', 'order_by', 'record_limit', 'calculation_type', 'default_icon', 'chart_theme',
                 'select_unit_type', 'custom_unit', 'show_unit', 'filter_date_field', 'chart_date_filter', 'show_legend',
                 'stack_options', 'show_custom_unit', 'chart_sub_groupby_id', 'chart_sub_groupby_type', 'chart_sub_groupby_date')
    def _compute_chart_data(self):
        for chart in self:
            ctx = self._context.copy()
            if chart.filter_date_field and chart.chart_date_filter == 'none' and ctx.get('date_filter_type', False):
                domain = eval(chart.generate_domain())
            else:
                domain = eval(chart.all_domain)

            order_by = chart.sort_by.name if chart.sort_by else "id"
            if chart.order_by:
                order_by = order_by + " " + chart.order_by
            limit = chart.record_limit if chart.record_limit else False

            colors = []
            if chart.chart_theme == 'light':
                colors.extend(['#94D994', '#F8C5C5', '#EEDD82', '#BFCDC6', '#A8ACFF', '#AD99FF',
                               '#eeaaee', '#d88383', '#7798BF', '#aaeeee'])
            elif chart.chart_theme == 'dark':
                colors.extend(['#ff0066', '#d733d7', '#55BF3B', '#db3939', '#486c99', '#23b3b3',
                               '#2b908f', '#68e84f', '#f0e628', '#9ea82e', '#29d1a7'])
            elif chart.chart_theme == 'multi':
                colors.extend(['#7cb5ec', '#94D994', '#2E5090', '#EEDD82', '#9E0508', '#F64D54',
                               '#A8ACFF', '#61B329', '#83F52C', '#BCED91'])

            chart_data = {
                'exporting': {
                    'buttons': {
                        'contextButton': {
                            'menuItems': ['viewFullscreen', 'printChart', 'downloadPNG', 'downloadJPEG',
                                          'downloadPDF', 'downloadSVG']
                        }
                    }
                }
            }
            if chart.chart_type in ['column', 'bar', 'line', 'area', 'polar'] and chart.chart_groupby_id and chart.chart_theme:
                chart_data.update({
                    'chart': {
                        'renderTo': 'chart_container',
                        'type': chart.chart_type,
                    },
                    'title': {
                        'text': _(chart.name)
                    },
                    'plotOptions': {'series': {}}
                })

                if chart.stack_options:
                    chart_data['plotOptions']['series'].update({'stacking': 'normal'})

                if chart.show_unit:
                    chart_data['plotOptions']['series'].update({'dataLabels': {'enabled': True, 'format': '{y}'}})
                    if chart.show_custom_unit and chart.select_unit_type == 'monetary':
                        currency = self.env.user.company_id.currency_id
                        if currency.position == 'after':
                            chart_data['plotOptions']['series']['dataLabels'].update({'format': '{y} ' + currency.symbol})
                        else:
                            chart_data['plotOptions']['series']['dataLabels'].update({'format': currency.symbol + ' {y}'})
                    elif chart.show_custom_unit and chart.select_unit_type == 'custom' and chart.custom_unit:
                        chart_data['plotOptions']['series']['dataLabels'].update({'format': '{y} ' + chart.custom_unit})

                if chart.chart_type == 'line':
                    chart_data['chart'].pop('type')

                if chart.chart_type == 'polar':
                    chart_data['chart']['polar'] = True
                    chart_data['chart']['type'] = 'column'

                categories = []
                series = []
                if chart.calculation_type == 'count' and chart.chart_groupby_id:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 1")
                    if chart.chart_groupby_type == 'relational_type':
                        all_fields = [chart.chart_groupby_id.name]
                        groupby_fields = [chart.chart_groupby_id.name]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit)
                        categories = [x[chart.chart_groupby_id.name] and x[chart.chart_groupby_id.name][1]._value or 'Undefined' for x in group_data]

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)

                        if chart.chart_theme in ['default', 'multi']:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(
                                    domain, [chart.chart_sub_groupby_id.name], groupby=[sub_group_by_field_name])

                                for sub_key in sub_group_key:
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:
                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y['__count'])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1] or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name, False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(sub_key[sub_group_by_field_name], 'Undefined')

                                    series_data = {'name': display_value, 'showInLegend': chart.show_legend and True or False, 'data': data}
                                    if chart.chart_theme == 'multi':
                                        series_data.update({'colorByPoint': True})
                                    series.append(series_data)
                            else:
                                series_data = {
                                    'name': chart.chart_groupby_id.field_description,
                                    'showInLegend': chart.show_legend and True or False,
                                    'data': [x[chart.chart_groupby_id.name + '_count'] for x in group_data]}
                                if chart.chart_theme == 'multi':
                                    series_data.update({'colorByPoint': True})
                                series.append(series_data)
                        else:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(domain, [chart.chart_sub_groupby_id.name],
                                                                                      groupby=[sub_group_by_field_name])
                                for i, sub_key in enumerate(sub_group_key):
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:

                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y['__count'])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1] or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name, False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(sub_key[sub_group_by_field_name], 'Undefined')

                                    series.append({'name': display_value, 'showInLegend': chart.show_legend and True or False, 'color': colors[(i + 1) % 10], 'data': data})
                            else:
                                series.append({
                                    'name': chart.chart_groupby_id.field_description,
                                    'showInLegend': chart.show_legend and True or False,
                                    'color': colors[0],
                                    'data': [x[chart.chart_groupby_id.name + '_count'] for x in group_data],
                                })

                    elif chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date:
                        all_fields = [chart.chart_groupby_id.name]
                        groupby_fields = [chart.chart_groupby_id.name + ':' + chart.chart_groupby_date]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields,
                                                                           orderby=order_by, limit=limit)
                        categories = [x.get(chart.chart_groupby_id.name + ':' + chart.chart_groupby_date, False) and x[chart.chart_groupby_id.name + ':' + chart.chart_groupby_date] or 'Undefined' for x in group_data]

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)

                        if chart.chart_theme in ['default', 'multi']:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(
                                    domain, [chart.chart_sub_groupby_id.name], groupby=[sub_group_by_field_name])

                                for sub_key in sub_group_key:
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:
                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y['__count'])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[
                                        sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1] or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name,
                                                     False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(
                                            self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(
                                            sub_key[sub_group_by_field_name], 'Undefined')

                                    series_data = {'name': display_value, 'showInLegend': chart.show_legend and True or False, 'data': data}
                                    if chart.chart_theme == 'multi':
                                        series_data.update({'colorByPoint': True})
                                    series.append(series_data)
                            else:
                                series_data = {
                                    'name': chart.chart_groupby_id.field_description,
                                    'showInLegend': chart.show_legend and True or False,
                                    'data': [x[chart.chart_groupby_id.name + '_count'] for x in group_data]}
                                if chart.chart_theme == 'multi':
                                    series_data.update({'colorByPoint': True})
                                series.append(series_data)
                        else:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(domain,
                                                                                      [chart.chart_sub_groupby_id.name],
                                                                                      groupby=[sub_group_by_field_name])
                                for i, sub_key in enumerate(sub_group_key):
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:

                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y['__count'])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[
                                        sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1] or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name,
                                                     False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(
                                            self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(
                                            sub_key[sub_group_by_field_name], 'Undefined')

                                    series.append({'name': display_value, 'showInLegend': chart.show_legend and True or False, 'color': colors[(i + 1) % 10], 'data': data})
                            else:
                                series.append({
                                    'name': chart.chart_groupby_id.field_description,
                                    'showInLegend': chart.show_legend and True or False,
                                    'color': colors[0],
                                    'data': [x[chart.chart_groupby_id.name + '_count'] for x in group_data],
                                })
                    else:
                        all_fields = [chart.chart_groupby_id.name]
                        groupby_fields = [chart.chart_groupby_id.name]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields,
                                                                           orderby=order_by, limit=limit)
                        categories = []
                        for data in group_data:
                            if chart.chart_groupby_id.ttype == 'selection':
                                selection_name = dict(self.env[chart.model_name]._fields[chart.chart_groupby_id.name].selection).get(data[chart.chart_groupby_id.name])
                                categories.append(selection_name)
                            else:
                                categories.append(data[chart.chart_groupby_id.name] and data[chart.chart_groupby_id.name] or 'Undefined')
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",chart.chart_sub_groupby_id)
                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)

                        if chart.chart_theme in ['default', 'multi']:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(
                                    domain, [chart.chart_sub_groupby_id.name], groupby=[sub_group_by_field_name])

                                for sub_key in sub_group_key:
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:
                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y['__count'])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[
                                        sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1]._value or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name,
                                                     False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(
                                            self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(
                                            sub_key[sub_group_by_field_name], 'Undefined')

                                    series_data = {'name': display_value, 'showInLegend': chart.show_legend and True or False, 'data': data}
                                    if chart.chart_theme == 'multi':
                                        series_data.update({'colorByPoint': True})
                                    series.append(series_data)
                            else:
                                series_data = {
                                    'name': chart.chart_groupby_id.field_description,
                                    'showInLegend': chart.show_legend and True or False,
                                    'data': [x[chart.chart_groupby_id.name + '_count'] for x in group_data]}
                                if chart.chart_theme == 'multi':
                                    series_data.update({'colorByPoint': True})
                                series.append(series_data)
                        else:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(domain,
                                                                                      [chart.chart_sub_groupby_id.name],
                                                                                      groupby=[sub_group_by_field_name])
                                for i, sub_key in enumerate(sub_group_key):
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:

                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y['__count'])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[
                                        sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1]._value or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name,
                                                     False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(
                                            self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(
                                            sub_key[sub_group_by_field_name], 'Undefined')

                                    series.append({'name': display_value, 'showInLegend': chart.show_legend and True or False, 'color': colors[(i + 1) % 10], 'data': data})
                            else:
                                series.append({
                                    'name': chart.chart_groupby_id.field_description,
                                    'showInLegend': chart.show_legend and True or False,
                                    'color': colors[0],
                                    'data': [x[chart.chart_groupby_id.name + '_count'] for x in group_data],
                                })

                    chart_data.update({
                        'xAxis': {
                            'categories': categories,
                        },
                        'yAxis': {
                            'title': {
                                'text': 'Record Count'
                            },
                        },
                        'credits': {
                            'enabled': False
                        },
                        'series': series
                    })

                elif chart.calculation_type == 'sum' and chart.chart_groupby_id:
                    measure_fields = [x.name for x in chart.chart_measure_field_ids]
                    if chart.chart_groupby_type == 'relational_type':
                        all_fields = [chart.chart_groupby_id.name] + measure_fields
                        groupby_fields = [chart.chart_groupby_id.name]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit)
                        categories = [x[chart.chart_groupby_id.name] and x[chart.chart_groupby_id.name][1]._value or 'Undefined' for x in group_data]

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)

                    elif chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date:
                        all_fields = [chart.chart_groupby_id.name] + measure_fields
                        groupby_fields = [chart.chart_groupby_id.name + ':' + chart.chart_groupby_date]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit)
                        for x in group_data:
                            for k, v in x.items():
                                if v and chart.chart_groupby_id.name + ':' in k:
                                        categories.append(x[k])
                                elif not v and chart.chart_groupby_id.name + ':' in k:
                                    categories.append("Undefined")

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                    else:
                        all_fields = [chart.chart_groupby_id.name] + measure_fields
                        groupby_fields = [chart.chart_groupby_id.name]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit)
                        categories = []
                        for data in group_data:
                            if chart.chart_groupby_id.ttype == 'selection':
                                selection_name = dict(self.env[chart.model_name]._fields[chart.chart_groupby_id.name].selection).get(data[chart.chart_groupby_id.name])
                                categories.append(selection_name)
                            else:
                                categories.append(data[chart.chart_groupby_id.name] and data[chart.chart_groupby_id.name] or 'Undefined')

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)

                    for i, measure in enumerate(chart.chart_measure_field_ids):
                        group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                        if chart.chart_theme in ['default', 'multi']:
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(domain, [chart.chart_sub_groupby_id.name], groupby=[sub_group_by_field_name])
                                for sub_key in sub_group_key:
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:
                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y[measure.name])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1]._value or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name, False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(sub_key[sub_group_by_field_name], 'Undefined')

                                    series_data = {'name': display_value + ' ' + measure.field_description, 'showInLegend': chart.show_legend and True or False, 'data': data}
                                    if chart.chart_theme == 'multi':
                                        series_data.update({'colorByPoint': True})
                                    series.append(series_data)
                            else:
                                series_data = {'name': measure.field_description,
                                               'showInLegend': chart.show_legend and True or False,
                                               'data': [x[measure.name] for x in group_data if x.get(measure.name, False)]}
                                if chart.chart_theme == 'multi':
                                    series_data.update({'colorByPoint': True})
                                series.append(series_data)
                        else:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(domain, [chart.chart_sub_groupby_id.name], groupby=[sub_group_by_field_name])
                                for i, sub_key in enumerate(sub_group_key):
                                    sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:
                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(y[measure.name])
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1]._value or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name, False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(sub_key[sub_group_by_field_name], 'Undefined')

                                    series.append({'name': display_value + ' ' + measure.field_description, 'showInLegend': chart.show_legend and True or False, 'color': colors[(i + 1) % 10], 'data': data})
                            else:
                                series.append({'name': measure.field_description,
                                               'showInLegend': chart.show_legend and True or False,
                                               'color': colors[(i + 1) % 10],
                                               'data': [x[measure.name] for x in group_data if x.get(measure.name, False)]})

                    chart_data.update({
                        'xAxis': {
                            'categories': categories
                        },
                        'credits': {
                            'enabled': False
                        },
                        'yAxis': {
                            'title': {
                                'text': 'Total'
                            }
                        },
                        'series': series
                    })
                elif chart.calculation_type == 'average' and chart.chart_groupby_id:
                    measure_fields = [x.name for x in chart.chart_measure_field_ids]
                    if chart.chart_groupby_type == 'relational_type':
                        all_fields = [chart.chart_groupby_id.name] + measure_fields
                        groupby_fields = [chart.chart_groupby_id.name]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields,
                                                                           orderby=order_by, limit=limit)
                        categories = [
                            x[chart.chart_groupby_id.name] and x[chart.chart_groupby_id.name][1]._value or 'Undefined' for x in
                            group_data]

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)

                    elif chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date:
                        all_fields = [chart.chart_groupby_id.name] + measure_fields
                        groupby_fields = [chart.chart_groupby_id.name + ':' + chart.chart_groupby_date]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields,
                                                                           orderby=order_by, limit=limit)
                        for x in group_data:
                            for k, v in x.items():
                                if v and chart.chart_groupby_id.name + ':' in k:
                                    categories.append(x[k])
                                elif not v and chart.chart_groupby_id.name + ':' in k:
                                    categories.append("Undefined")

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                    else:
                        all_fields = [chart.chart_groupby_id.name] + measure_fields
                        groupby_fields = [chart.chart_groupby_id.name]
                        group_data = self.env[chart.model_name].read_group(domain, all_fields, groupby=groupby_fields,
                                                                           orderby=order_by, limit=limit)
                        categories = []
                        for data in group_data:
                            if chart.chart_groupby_id.ttype == 'selection':
                                selection_name = dict(self.env[chart.model_name]._fields[chart.chart_groupby_id.name].selection).get(data[chart.chart_groupby_id.name])
                                categories.append(selection_name)
                            else:
                                categories.append(data[chart.chart_groupby_id.name] and data[
                                    chart.chart_groupby_id.name] or 'Undefined')

                        if chart.chart_sub_groupby_id:
                            all_fields += [chart.chart_sub_groupby_id.name]
                            if chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_date:
                                groupby_fields += [chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)
                            else:
                                groupby_fields += [chart.chart_sub_groupby_id.name]
                                sub_group_data = self.env[chart.model_name].read_group(
                                    domain, all_fields, groupby=groupby_fields, orderby=order_by, limit=limit,
                                    lazy=False)

                    for i, measure in enumerate(chart.chart_measure_field_ids):
                        group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                        if chart.chart_theme in ['default', 'multi']:
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(domain,
                                                                                      [chart.chart_sub_groupby_id.name],
                                                                                      groupby=[sub_group_by_field_name])
                                for sub_key in sub_group_key:
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:
                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(float("{0:.2f}".format(y[measure.name] / y['__count'])))
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[
                                        sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1]._value or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name,
                                                     False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(
                                            self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(
                                            sub_key[sub_group_by_field_name], 'Undefined')

                                    series_data = {'name': display_value + ' ' + measure.field_description, 'showInLegend': chart.show_legend and True or False, 'data': data}
                                    if chart.chart_theme == 'multi':
                                        series_data.update({'colorByPoint': True})
                                    series.append(series_data)
                            else:
                                series_data = {'name': measure.field_description,
                                               'showInLegend': chart.show_legend and True or False,
                                               'data': [float("{0:.2f}".format(x[measure.name] / x[chart.chart_groupby_id.name + '_count'])) for x in group_data if x.get(measure.name, False)]}
                                if chart.chart_theme == 'multi':
                                    series_data.update({'colorByPoint': True})
                                series.append(series_data)
                        else:
                            group_by_field_name = (chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date) and chart.chart_groupby_id.name + ':' + chart.chart_groupby_date or chart.chart_groupby_id.name
                            if chart.chart_sub_groupby_id:
                                sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                sub_group_key = self.env[chart.model_name].read_group(domain,
                                                                                      [chart.chart_sub_groupby_id.name],
                                                                                      groupby=[sub_group_by_field_name])
                                for i, sub_key in enumerate(sub_group_key):
                                    sub_group_by_field_name = chart.chart_sub_groupby_type == 'date_type' and chart.chart_sub_groupby_id.name + ':' + chart.chart_sub_groupby_date or chart.chart_sub_groupby_id.name
                                    data = []
                                    for x in group_data:
                                        no_data = False
                                        for y in sub_group_data:
                                            if x[group_by_field_name] == y[group_by_field_name] and sub_key[sub_group_by_field_name] == y[sub_group_by_field_name]:
                                                data.append(float("{0:.2f}".format(y[measure.name] / y['__count'])))
                                                no_data = True
                                        if not no_data:
                                            data.append('Null')

                                    display_value = sub_key.get(sub_group_by_field_name, False) and sub_key[
                                        sub_group_by_field_name] or 'Undefined'
                                    if chart.chart_sub_groupby_type == 'relational_type':
                                        display_value = sub_key[sub_group_by_field_name] and sub_key[sub_group_by_field_name][1]._value or "Undefined"
                                    elif sub_key.get(sub_group_by_field_name,
                                                     False) and chart.chart_sub_groupby_id.ttype == 'selection':
                                        display_value = dict(
                                            self.env[chart.model_name]._fields[sub_group_by_field_name].selection).get(
                                            sub_key[sub_group_by_field_name], 'Undefined')

                                    series.append({'name': display_value + ' ' + measure.field_description, 'showInLegend': chart.show_legend and True or False, 'color': colors[(i + 1) % 10], 'data': data})
                            else:
                                series.append({'name': measure.field_description,
                                               'showInLegend': chart.show_legend and True or False,
                                               'color': colors[(i + 1) % 10],
                                               'data': [float("{0:.2f}".format(x[measure.name] / x[chart.chart_groupby_id.name + '_count'])) for x in group_data if x.get(measure.name, False)]})

                    chart_data.update({
                        'xAxis': {
                            'categories': categories
                        },
                        'credits': {
                            'enabled': False
                        },
                        'yAxis': {
                            'title': {
                                'text': 'Total'
                            }
                        },
                        'series': series
                    })
            elif chart.chart_type in ['pie'] and chart.chart_groupby_id:
                series = []
                chart_data.update({
                    'chart': {
                        'plotBackgroundColor': False,
                        'plotBorderWidth': False,
                        'plotShadow': False,
                        'renderTo': 'chart_container',
                        'type': chart.chart_type,

                    },
                    'title': {
                        'text': _(chart.name)
                    },
                    'credits': {
                        'enabled': False
                    },
                    'plotOptions': {
                        'pie': {
                            'allowPointSelect': True,
                            'cursor': 'pointer',
                            'showInLegend': chart.show_legend and True or False,
                        }
                    },
                    'series': []
                })

                if chart.show_unit:
                    chart_data['plotOptions']['pie'].update({'dataLabels': {'enabled': True, 'format': '{y}'}})
                    if chart.show_custom_unit and chart.select_unit_type == 'monetary':
                        currency = self.env.user.company_id.currency_id
                        if currency.position == 'after':
                            chart_data['plotOptions']['pie']['dataLabels'].update({'format': '{y} ' + currency.symbol})
                        else:
                            chart_data['plotOptions']['pie']['dataLabels'].update({'format': currency.symbol + ' {y}'})
                    elif chart.show_custom_unit and chart.select_unit_type == 'custom' and chart.custom_unit:
                        chart_data['plotOptions']['pie']['dataLabels'].update({'format': '{y} ' + chart.custom_unit})

                if chart.calculation_type == 'count':
                    if chart.chart_groupby_type == 'relational_type':
                        all_data = self.env[chart.model_name].read_group(domain,
                                                                         [chart.chart_groupby_id.name],
                                                                         groupby=[chart.chart_groupby_id.name],
                                                                         orderby=order_by, limit=limit)
                        series.append({'data': [
                            {'name': x.get(chart.chart_groupby_id.name, False) and x[chart.chart_groupby_id.name][1]._value or 'Undefinded', 'y': x[chart.chart_groupby_id.name + '_count']} for
                            x in all_data]})
                        chart_data['series'] = series
                    elif chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date:
                        all_data = self.env[chart.model_name].read_group(
                            domain, [chart.chart_groupby_id.name], groupby=[chart.chart_groupby_id.name + ':' + chart.chart_groupby_date], orderby=order_by, limit=limit)
                        for x in all_data:
                            for k, v in x.items():
                                if v and (chart.chart_groupby_id.name + ':') in k:
                                    series.append({'name': x[k], 'y': x[chart.chart_groupby_id.name + '_count']})
                                elif not v and (chart.chart_groupby_id.name + ':') in k:
                                    series.append({'name': 'Undefined', 'y': x[chart.chart_groupby_id.name + '_count']})
                        chart_data['series'] = [{'data': series}]
                    else:
                        all_data = self.env[chart.model_name].read_group(
                            domain, [chart.chart_groupby_id.name], groupby=[chart.chart_groupby_id.name], orderby=order_by, limit=limit)
                        for data in all_data:
                            if chart.chart_groupby_id.ttype == 'selection':
                                selection_name = dict(self.env[chart.model_name]._fields[chart.chart_groupby_id.name].selection).get(data[chart.chart_groupby_id.name])
                                series.append({'name': selection_name, 'y': data[chart.chart_groupby_id.name + '_count']})
                            else:
                                series.append({'name': data[chart.chart_groupby_id.name], 'y': data[chart.chart_groupby_id.name + '_count']})
                        chart_data['series'] = [{'data': series}]

                elif chart.calculation_type == 'sum' and chart.chart_measure_field_ids:
                    measure_fields = [x.name for x in chart.chart_measure_field_ids]
                    if chart.chart_groupby_type == 'relational_type':
                        all_data = self.env[chart.model_name].read_group(domain,
                                                                         [chart.chart_groupby_id.name] + measure_fields,
                                                                         groupby=[chart.chart_groupby_id.name],
                                                                         orderby=order_by, limit=limit)

                        series.append({'name': chart.chart_measure_field_ids[0].field_description, 'data': [
                            {'name': x.get(chart.chart_groupby_id.name, False) and x[chart.chart_groupby_id.name][1]._value or 'Undefinded', 'y': x[chart.chart_measure_field_ids[0].name]} for
                            x in all_data]})
                        chart_data['series'] = series
                    elif chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date:
                        all_data = self.env[chart.model_name].read_group(domain,
                                                                         [chart.chart_groupby_id.name] + measure_fields,
                                                                         groupby=[
                                                                             chart.chart_groupby_id.name + ':' + chart.chart_groupby_date],
                                                                         orderby=order_by, limit=limit)
                        for x in all_data:
                            if x[chart.chart_groupby_id.name + ':' + chart.chart_groupby_date]:
                                series.append(
                                    {'name': x[chart.chart_groupby_id.name + ':' + chart.chart_groupby_date],
                                     'y': x[chart.chart_measure_field_ids[0].name]})
                            else:
                                series.append(
                                    {'name': 'Undefined',
                                     'y': x[chart.chart_measure_field_ids[0].name]})

                        chart_data['series'].append(
                            {'name': chart.chart_measure_field_ids[0].field_description, 'data': series})
                    else:
                        all_data = self.env[chart.model_name].read_group(
                            domain, [chart.chart_groupby_id.name] + measure_fields,
                            groupby=[chart.chart_groupby_id.name], orderby=order_by, limit=limit)

                        if chart.chart_groupby_id.ttype == 'selection':
                            series.append({'name': chart.chart_measure_field_ids[0].field_description, 'data': [
                                {'name': dict(self.env[chart.model_name]._fields[chart.chart_groupby_id.name].selection).get(x[chart.chart_groupby_id.name]), 'y': x[chart.chart_measure_field_ids[0].name]} for x in all_data]})
                        else:
                            series.append({'name': chart.chart_measure_field_ids[0].field_description, 'data': [
                                {'name': x[chart.chart_groupby_id.name], 'y': x[chart.chart_measure_field_ids[0].name]} for x in all_data]})

                        chart_data['series'] = series

                elif chart.calculation_type == 'average' and chart.chart_measure_field_ids:
                    measure_fields = [x.name for x in chart.chart_measure_field_ids]
                    if chart.chart_groupby_type == 'relational_type':
                        all_data = self.env[chart.model_name].read_group(domain,
                                                                         [chart.chart_groupby_id.name] + measure_fields,
                                                                         groupby=[chart.chart_groupby_id.name],
                                                                         orderby=order_by, limit=limit)

                        series.append({'name': chart.chart_measure_field_ids[0].field_description, 'data': [
                            {'name': x.get(chart.chart_groupby_id.name, False) and x[chart.chart_groupby_id.name][1]._value or 'Undefinded',
                             'y': float("{0:.2f}".format(x[chart.chart_measure_field_ids[0].name] / x[chart.chart_groupby_id.name + '_count']))} for
                            x in all_data]})
                        chart_data['series'] = series
                    elif chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date:
                        all_data = self.env[chart.model_name].read_group(domain,
                                                                         [chart.chart_groupby_id.name] + measure_fields,
                                                                         groupby=[
                                                                             chart.chart_groupby_id.name + ':' + chart.chart_groupby_date],
                                                                         orderby=order_by, limit=limit)
                        for x in all_data:
                            if x[chart.chart_groupby_id.name + ':' + chart.chart_groupby_date]:
                                series.append(
                                    {'name': x[chart.chart_groupby_id.name + ':' + chart.chart_groupby_date],
                                     'y': x[chart.chart_measure_field_ids[0].name] / x[
                                         chart.chart_groupby_id.name + '_count']})
                            else:
                                series.append(
                                    {'name': 'Undefined',
                                     'y': x[chart.chart_measure_field_ids[0].name] / x[
                                         chart.chart_groupby_id.name + '_count']})

                        chart_data['series'].append(
                            {'name': chart.chart_measure_field_ids[0].field_description, 'data': series})
                    else:
                        all_data = self.env[chart.model_name].read_group(
                            domain, [chart.chart_groupby_id.name] + measure_fields,
                            groupby=[chart.chart_groupby_id.name], orderby=order_by, limit=limit)

                        if chart.chart_groupby_id.ttype == 'selection':
                            series.append({'name': chart.chart_measure_field_ids[0].field_description, 'data': [
                                {'name': dict(self.env[chart.model_name]._fields[chart.chart_groupby_id.name].selection).get(x[chart.chart_groupby_id.name]), 'y': x[chart.chart_measure_field_ids[0].name] / x[chart.chart_groupby_id.name + '_count']} for x in all_data]})
                        else:
                            series.append({'name': chart.chart_measure_field_ids[0].field_description, 'data': [
                                {'name': x[chart.chart_groupby_id.name], 'y': x[chart.chart_measure_field_ids[0].name] / x[chart.chart_groupby_id.name + '_count']} for x in all_data]})

                        chart_data['series'] = series
            elif chart.chart_type in ['list_view'] and chart.model_name:
                all_rows = []
                header = []
                if chart.list_view_type == 'ungrouped':
                    header = [_(x.field_description) for x in chart.list_view_fields]
                    all_data = self.env[chart.model_name].search_read(domain,
                                                                      [x.name for x in chart.list_view_fields],
                                                                      order=order_by, limit=limit)
                    for data in all_data:
                        row_data = []
                        for f in chart.list_view_fields:
                            if f.ttype == 'many2one':
                                row_data.append(data.get(f.name, False) and data[f.name][1] or '')
                            elif f.ttype in ['integer', 'float', 'monetary']:
                                row_data.append(data.get(f.name, False) and formatLang(self.env, data[f.name]) or 0)
                            elif f.ttype in ['date', 'datetime']:
                                row_data.append(data.get(f.name, False) and fields.Date.to_string(data[f.name]) or '')
                            else:
                                row_data.append(data.get(f.name, False) and data[f.name] or '')

                        all_rows.append(row_data)
                elif chart.list_view_type == 'grouped' and chart.chart_groupby_id:
                    if chart.chart_groupby_type == 'relational_type':
                        header = [_(chart.chart_groupby_id.field_description)] + [_(x.field_description) for x in chart.list_view_group_fields]
                        all_data = self.env[chart.model_name].read_group(domain,
                                                                         [chart.chart_groupby_id.name] + [x.name for x in
                                                                                                          chart.list_view_group_fields],
                                                                         groupby=[chart.chart_groupby_id.name],
                                                                         orderby=order_by, limit=limit)
                        for data in all_data:
                            row_data = [
                                data.get(chart.chart_groupby_id.name, False) and data[chart.chart_groupby_id.name][1]._value or '']

                            for f in chart.list_view_group_fields:
                                if f.ttype == 'many2one':
                                    row_data.append(data.get(f.name, False) and data[f.name][1] or '')
                                elif f.ttype in ['integer', 'float', 'monetary']:
                                    row_data.append(data.get(f.name, False) and formatLang(self.env, data[f.name]) or 0)
                                elif f.ttype in ['date', 'datetime']:
                                    row_data.append(data.get(f.name, False) and fields.Date.to_string(data[f.name]) or '')
                                else:
                                    row_data.append(data.get(f.name, False) and data[f.name] or '')
                            all_rows.append(row_data)

                    elif chart.chart_groupby_type == 'date_type' and chart.chart_groupby_date:
                        header = [chart.chart_groupby_id.field_description] + [x.field_description for x in
                                                                               chart.list_view_group_fields]
                        all_data = self.env[chart.model_name].read_group(domain, [chart.chart_groupby_id.name] + [x.name for x in chart.list_view_group_fields],
                                                                         groupby=[chart.chart_groupby_id.name + ':' + chart.chart_groupby_date],
                                                                         orderby=order_by, limit=limit)
                        for data in all_data:
                            row_data = [
                                data.get(chart.chart_groupby_id.name + ':' + chart.chart_groupby_date, False) and data[
                                    chart.chart_groupby_id.name + ':' + chart.chart_groupby_date] or 'Undefined']

                            for f in chart.list_view_group_fields:
                                if f.ttype == 'many2one':
                                    row_data.append(data.get(f.name, False) and data[f.name][1] or '')
                                elif f.ttype in ['integer', 'float', 'monetary']:
                                    row_data.append(data.get(f.name, False) and formatLang(self.env, data[f.name]) or 0)
                                elif f.ttype in ['date', 'datetime']:
                                    row_data.append(data.get(f.name, False) and fields.Date.to_string(data[f.name]) or '')
                                else:
                                    row_data.append(data.get(f.name, False) and data[f.name] or '')
                            all_rows.append(row_data)
                    else:
                        header = [chart.chart_groupby_id.field_description] + [x.field_description for x in chart.list_view_group_fields]
                        all_data = self.env[chart.model_name].read_group(domain, [chart.chart_groupby_id.name] + [x.name for x in chart.list_view_group_fields],
                                                                         groupby=[chart.chart_groupby_id.name],
                                                                         orderby=order_by, limit=limit)
                        for data in all_data:
                            if chart.chart_groupby_id.ttype == 'selection':
                                row_data = [data.get(chart.chart_groupby_id.name, False) and dict(self.env[chart.model_name]._fields[chart.chart_groupby_id.name].selection).get(data[chart.chart_groupby_id.name]) or '']
                            else:
                                row_data = [data.get(chart.chart_groupby_id.name, False) and data[chart.chart_groupby_id.name] or '']

                            for f in chart.list_view_group_fields:
                                if f.ttype == 'many2one':
                                    row_data.append(data.get(f.name, False) and data[f.name][1] or '')
                                elif f.ttype in ['integer', 'float', 'monetary']:
                                    row_data.append(data.get(f.name, False) and formatLang(self.env, data[f.name]) or 0)
                                elif f.ttype in ['date', 'datetime']:
                                    row_data.append(data.get(f.name, False) and fields.Date.to_string(data[f.name]) or '')
                                else:
                                    row_data.append(data.get(f.name, False) and data[f.name] or '')
                            all_rows.append(row_data)
                chart_data = {'header': header, 'row_data': all_rows}
            print(">>>>>>>>>>>>>>>>",chart_data)
            chart.chart_data = json.dumps(chart_data)

    @api.depends('total_record', 'data_comparision', 'kpi_target', 'kpi_target_value', 'kpi_target_view_type',
                 'second_calculation_type', 'second_model_id', 'second_domain', 'second_record_field',
                 'second_filter_date_field', 'second_date_filter')
    def _compute_second_total_record(self):
        print('?????>>>>>>>>>',self)
        for chart in self:
            print(dir(chart))
            print(chart.second_total_record)
            print(chart.target_display_value,chart.target_value_type,chart.progress_bar_value,chart.progress_bar_max)
            if chart.second_model_id:
                ctx = self._context.copy()
                model_domain = date_filter = []
                if chart.second_filter_date_field and chart.second_date_filter == 'none' and ctx.get('date_filter_type', False) and ctx['date_filter_type'] != 'none':
                    if ctx['date_filter_type'] == 'custom' and ctx.get('custom_start_date', False) and ctx.get('custom_end_date', False):
                        start_date = datetime.strptime(ctx['custom_start_date'], '%m/%d/%Y').replace(hour=0, minute=0, second=0, microsecond=0)
                        end_date = datetime.strptime(ctx['custom_end_date'], '%m/%d/%Y').replace(hour=23, minute=59, second=59, microsecond=0)
                        date_filter = [(chart.filter_date_field.name, ">=", fields.Datetime.to_string(start_date)),
                                       (chart.filter_date_field.name, "<=", fields.Datetime.to_string(end_date))]
                    else:
                        filter_dates = chart.get_filter_start_and_end_date(ctx['date_filter_type'])
                        start_date = filter_dates[0]
                        end_date = filter_dates[1]
                        date_filter = [(chart.filter_date_field.name, ">=", fields.Datetime.to_string(start_date)),
                                       (chart.filter_date_field.name, "<=", fields.Datetime.to_string(end_date))]
                elif chart.second_filter_date_field and chart.second_date_filter != 'none':
                    filter_dates = chart.get_filter_start_and_end_date(chart.second_date_filter)
                    start_date = filter_dates[0]
                    end_date = filter_dates[1]
                    date_filter = [(chart.filter_date_field.name, ">=", fields.Datetime.to_string(start_date)),
                                   (chart.filter_date_field.name, "<=", fields.Datetime.to_string(end_date))]

                if chart.second_domain and "%UID" in chart.second_domain:
                    model_domain = eval(chart.second_domain.replace('"%UID"', str(self.env.user.id)))
                elif chart.second_domain:
                    model_domain = eval(chart.second_domain)

                domain = model_domain and (model_domain + date_filter) or ([] + date_filter)

                if chart.second_calculation_type == 'count' and chart.second_model_id:
                    chart.second_total_record = self.env[chart.second_model_id.model].search_count(domain)
                elif chart.second_calculation_type == 'sum' and chart.second_model_id and chart.second_record_field:
                    records = self.env[chart.second_model_id.model].search(domain)
                    chart.second_total_record = sum([x[chart.second_record_field.name] for x in records])
                elif chart.second_calculation_type == 'average' and chart.second_model_id and chart.second_record_field:
                    total_record = self.env[chart.second_model_id.model].search_count(domain)
                    records = self.env[chart.second_model_id.model].search(domain)
                    total_sum = sum([x[chart.second_record_field.name] for x in records])
                    if total_sum > 0:
                        chart.second_total_record = total_sum / total_record
                    else:
                        chart.second_total_record = 0
                else:
                    chart.second_total_record = 0

                if chart.data_comparision == 'none':
                    chart.kpi_value = str('%.2f' % (chart.total_record)) + '/' + str(
                        '%.2f' % (chart.second_total_record))
                elif chart.data_comparision == 'sum':
                    chart.kpi_value = str('%.2f' % (chart.total_record + chart.second_total_record))
                    if chart.kpi_target_value and chart.kpi_target_value > 0 and chart.kpi_target_view_type == 'number':
                        display_value = round(
                            (chart.total_record + chart.second_total_record) / chart.kpi_target_value * 100 - 100)
                        if display_value < 0:
                            chart.target_display_value = str(abs(display_value)) + '%'
                            chart.target_value_type = 'negative'
                        else:
                            chart.target_display_value = str(display_value) + '%'
                            chart.target_value_type = 'positive'

                    elif chart.kpi_target_value and chart.kpi_target_value > 0 and chart.kpi_target_view_type == 'progress_bar':
                        chart.kpi_value += ' / ' + str(chart.kpi_target_value)
                        cal_target_value = round(
                            (chart.total_record + chart.second_total_record) / chart.kpi_target_value * 100)
                        chart.target_display_value = str(cal_target_value) + '%'
                        if cal_target_value > 100:
                            chart.progress_bar_value = 100
                            chart.progress_bar_max = 100
                        else:
                            chart.progress_bar_value = cal_target_value
                            chart.progress_bar_max = 100
                elif chart.data_comparision == 'ratio' and chart.second_record_field:
                    chart.kpi_value = calculate_aspect(chart.total_record, chart.second_total_record)
                elif chart.data_comparision == 'percentage' and chart.second_total_record:
                    chart.kpi_value = chart.total_record and str(
                        round((chart.total_record * 100) / chart.second_total_record)) + '%' or '0%'
                    if chart.kpi_target_value and chart.kpi_target_value > 0 and chart.kpi_target_view_type == 'number':
                        display_value = round(
                            (chart.total_record + chart.second_total_record) / chart.kpi_target_value * 100 - 100)
                        if display_value < 0:
                            chart.target_display_value = str(abs(display_value)) + '%'
                            chart.target_value_type = 'negative'
                        else:
                            chart.target_display_value = str(display_value) + '%'
                            chart.target_value_type = 'positive'

                    elif chart.kpi_target_value and chart.kpi_target_value > 0 and chart.kpi_target_view_type == 'progress_bar':
                        chart.kpi_value += ' / ' + str(
                            round(chart.kpi_target_value < 100 and chart.kpi_target_value or 100)) + '%'

                        cal_target_value = round((chart.total_record * 100) / chart.second_total_record)
                        chart.target_display_value = str(cal_target_value) + '%'
                        chart.progress_bar_value = cal_target_value
                        chart.progress_bar_max = 100
            else:
                chart.kpi_value = chart.total_record
                if chart.kpi_target_value and chart.kpi_target_value > 0 and chart.kpi_target_view_type == 'number':
                    display_value = round((chart.total_record) / chart.kpi_target_value * 100 - 100)
                    if display_value < 0:
                        chart.target_display_value = str(abs(display_value)) + '%'
                        chart.target_value_type = 'negative'
                    else:
                        chart.target_display_value = str(display_value) + '%'
                        chart.target_value_type = 'positive'

                elif chart.kpi_target_value and chart.kpi_target_value > 0 and chart.kpi_target_view_type == 'progress_bar':
                    chart.kpi_value += ' / ' + str(chart.kpi_target_value)
                    cal_target_value = round(chart.total_record / chart.kpi_target_value * 100)
                    chart.target_display_value = str(cal_target_value) + '%'
                    if cal_target_value > 100:
                        chart.progress_bar_value = 100
                        chart.progress_bar_max = 100
                    else:
                        chart.progress_bar_value = cal_target_value
                        chart.progress_bar_max = 100

    def duplicate_dashboard_chart(self, dashboard_id):
        for chart in self:
            new_chart = chart.sudo().copy()
            new_chart.dashboard_id = dashboard_id

    def move_dashboard_chart(self, dashboard_id):
        for chart in self:
            chart.dashboard_id = dashboard_id
