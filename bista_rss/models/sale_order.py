# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rss_state = fields.Selection(string="RSS Status", selection=[('pending', 'Pending'), ('completed', 'Completed'), ],
                                 required=False, )
    customer_category_id = fields.Many2many(related='partner_id.category_id', string="Customer Tags")
