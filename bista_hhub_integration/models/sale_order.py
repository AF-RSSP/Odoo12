# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_hhub_order = fields.Boolean('Is HHub Order')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    hhub_line_id = fields.Integer('HHub Line ID')


