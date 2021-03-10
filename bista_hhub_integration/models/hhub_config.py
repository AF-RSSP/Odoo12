# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.bista_hhub_integration.models.connection import HhubConService


class HhubConfig(models.Model):
    _name = 'hhub.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hhub Configuration'

    name = fields.Char(string='HHub Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    environment = fields.Selection([
        ('test', 'Test'),
        ('production', 'Production')], default="test")
    api_key = fields.Char("API Key")
    secret_key = fields.Char("Secret Key")
    order_url = fields.Char("Order URL", default="/order/test")
    product_url = fields.Char("Product URL", default="/product/test")
    stock_url = fields.Char("Stock URL", default="/stock/test")
    dispatch_url = fields.Char("Dispatch URL", default="/dispatch/test")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    last_import_product_id = fields.Many2one('product.product', string='Last Import Product')
    last_import_product_date = fields.Date(string='Last Import Product Date')
    last_import_sale_order_id = fields.Many2one('sale.order', string='Last Import Sale Order')
    last_import_sale_order_date = fields.Date(string='Last Import Sale Order Date')

    _sql_constraints = [('hhub_config_company_unique', 'unique(company_id)', 'Hhub Configuration must be unique per company!')]

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hhub.config') or _('New')
        return super(HhubConfig, self).create(vals)

    @api.onchange('environment')
    def onchange_environment(self):
        if not self.environment:
            return
        if self.environment == 'test':
            # self.order_url = 'https://api-hhubstg3.hhglobal.com/V1/CatalogueOrder/All'
            # self.product_url = 'https://api-hhubstg3.hhglobal.com/V1/Product/All'
            # self.stock_url = '/stock/test'
            self.dispatch_url = 'https://api-hhubstg3.hhglobal.com/V1/Dispatches'
        if self.environment == 'production':
            # self.order_url = '/order/prod'
            # self.product_url = '/product/prod'
            # self.stock_url = '/stock/prod'
            self.dispatch_url = 'https://api-hhub.hhglobal.com/V1/Dispatches'

    # def import_product(self):
    #     self.ensure_one()
    #     products = HhubConService.get_product_api(self, self.product_url, self.api_key, self.secret_key)

    def import_sale_order(self):
        self.ensure_one()
        orders = HhubConService.get_order_api(self, self.order_url, self.api_key, self.secret_key)

    @api.model
    def _product_sale_order_import(self):
        pass
