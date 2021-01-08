# -*- coding: utf-8 -*-
{
    'name': "bista_hhub_integration",
    'summary': """This modules handles the requirement of RSS and HHUB Integration.""",
    'description': """This Module import the Sale Order from HHUB into RSS ODOO System and Exports the Dispatch Information back to the HHUB.
    """,
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Sale & Warehouse',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'stock', 'sale_stock'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/hhub_config_cron.xml',
        'views/hhub_config_views.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
