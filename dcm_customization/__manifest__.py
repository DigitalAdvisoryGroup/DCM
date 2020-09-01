# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': "DCM - Customization",
    'version': '1.0',
    'summary': """
        Odoo customizations for JustThis project requirements (http://www.xplain.ch/wp/produkte/justthis/)
    """,
    'description': """

DCM - Customization
===================
DCM - Customization

Description
-----------

    """,

    'author': "Digital Advisory Group GmbH, Candidroot Solutions Pvt. Ltd.",
    'website': "https://www.digitaladvisorygroup.io/",
    'category': 'Social',
    'depends': ['social','website','portal'],
    'data': [
        'security/security.xml',
        "security/ir.model.access.csv",
        "data/bit_media_data.xml",
        "data/mail_template_data.xml",
        "views/social_bit_templates.xml",
        "views/social_post_views.xml",
        "views/social_stream_post_views.xml",
        "views/social_groups_view.xml",
        "views/res_config_settings_view.xml",
        "views/portal_views.xml",
        "views/assets.xml",
    ],
    'demo': [
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}
