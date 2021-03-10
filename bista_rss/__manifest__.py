# -*- coding: utf-8 -*-
{
    'name': "bista_rss",
    'summary': """Imports the Sale Order by Uploading Excel File.""",
    'description': """Imports the Sale Order by Uploading Excel File""",
    'author': "Bista Solutions Private Ltd.",
    'website': "http://www.bistasolutions.com",
    'category': 'Sale',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','sale','product'],
    # always loaded
    'data': [
        'views/sale_view.xml',
        'views/volume_view.xml',
        'wizard/import_order_view.xml',
    ],
}
