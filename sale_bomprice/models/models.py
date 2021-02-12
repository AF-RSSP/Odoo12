# -*- coding: utf-8 -*-

from odoo import models, fields, api


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

    @api.depends('product_id', 'purchase_price', 'product_uom_qty',
                 'price_unit', 'price_subtotal')
    def _product_margin(self):
        if not self.env.in_onchange:
            # prefetch the fields needed for the computation
            self.read(['price_subtotal', 'purchase_price', 'product_uom_qty',
                       'order_id'])
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            price = line.purchase_price
            if line.price_subtotal:
                profit = currency.round(
                    line.price_subtotal - (price * line.product_uom_qty))
                sale_margin = line.price_unit * line.product_uom_qty
                line.margin = profit / sale_margin


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.margin')
    def _product_margin(self):
        # if self.env.in_onchange:
        for order in self:
            margin_sum = sum(order.order_line.filtered(
                lambda r: r.state != 'cancel').mapped('margin'))
            total_margin = 0
            amount_order = 0
            for line in order.order_line:
                total_margin += order.pricelist_id.currency_id.round(
                    line.price_subtotal - (
                                line.purchase_price * line.product_uom_qty))
                amount_order += line.price_unit * line.product_uom_qty
            if margin_sum:
                order.margin = total_margin / amount_order
