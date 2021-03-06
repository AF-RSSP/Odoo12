# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api
    
class SaleOrderLine(models.Model):
    _inherit="sale.order.line"
    
    @api.multi
    def pricelist_apply(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.pricelist.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

        