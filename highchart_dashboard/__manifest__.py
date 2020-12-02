# -*- coding: utf-8 -*-

{
    'name': "Highcharts",
    'version': '11.0.1.0.0',
    'summary': """ Dynamic Dashboard Module
    """,
    'description': """
    """,
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://www.candidroot.com/",
    'category': 'Tools',
    'depends': ['web', 'web_widget_color'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/dashboard_export_wizard_view.xml',
        'wizard/import_dashboard_wizard_view.xml',
        'views/assets.xml',
        'views/highchart_dashboard_views.xml',
        'views/highchart_dashboard_chart_views.xml',
        'views/menuitem.xml',
    ],
    'demo': [
        # 'demo/dashboard_demo.xml',
    ],
    'qweb': [
        'static/src/xml/base_import.xml',
        'static/src/xml/highchart_templates.xml',
        'static/src/xml/icon_view_widget.xml',
        'static/src/xml/tile_templates.xml',
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False
}
