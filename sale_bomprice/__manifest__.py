# -*- coding: utf-8 -*-
{
    'name': "BOM Price On Sale Order Line",

    'summary': """
        BOM Cost and Structure unit cost on sale order line for product cost""",

    'description': """
        Fetch the bom cost on the sale oder line cost field and added the
        formula for the sales margin
    """,

    'author': "Bista Solutions PVT LTD",
    'website': "http://www.bistasolutions.com",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'mrp_bom_cost', 'sale_margin'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
