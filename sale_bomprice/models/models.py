# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id and self.product_id.product_tmpl_id.bom_count > 0:
            self.product_id.button_bom_cost()
        return super(SaleOrderLine, self).product_id_change()

    @api.multi
    @api.onchange('product_uom_qty', 'product_id')
    def product_uom_qty_bom(self):
        if self.product_uom_qty and self.product_id:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id)
            if bom:
                res = self.env[
                    'report.mrp.report_bom_structure']._get_report_data(
                    bom_id=bom.id, searchQty=self.product_uom_qty,
                    searchVariant=False)
                self.purchase_price = res['lines']['total'] / res['lines'][
                    'bom_qty']
                self.price_unit = self.purchase_price / 0.40

    @api.depends('product_id', 'purchase_price', 'product_uom_qty',
                 'price_unit', 'price_subtotal')
    def _product_margin(self):
        super(SaleOrderLine, self)._product_margin()
        for line in self:
            if line.product_id:
                bom = self.env['mrp.bom']._bom_find(product=line.product_id)
                if bom:
                    res = self.env[
                        'report.mrp.report_bom_structure']._get_report_data(
                        bom_id=bom.id, searchQty=line.product_uom_qty,
                        searchVariant=False)
                    line.purchase_price = res['lines']['total'] / res['lines'][
                        'bom_qty']
                    line.price_unit = line.purchase_price / 0.40

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        super(SaleOrderLine, self).product_uom_change()
        bom = self.env['mrp.bom']._bom_find(product=self.product_id)
        if bom:
            res = self.env[
                'report.mrp.report_bom_structure']._get_report_data(
                bom_id=bom.id, searchQty=self.product_uom_qty,
                searchVariant=False)
            self.purchase_price = res['lines']['total'] / res['lines'][
                'bom_qty']
            self.price_unit = self.purchase_price / 0.40


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    margin_per = fields.Float(compute='_product_margin_per', string="Margin %",
                              digits=dp.get_precision('Product Price'))


    @api.depends('amount_total','margin')
    def _product_margin_per(self):
        for order in self:
            if order:
                if order.margin and order.amount_total:
                    order.margin_per = order.margin / order.amount_total
