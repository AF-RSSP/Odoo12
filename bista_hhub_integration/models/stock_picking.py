# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.bista_hhub_integration.models.connection import HhubConService


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def check_done_quantity(self, sale_order):
        for line in sale_order.order_line:
            if line.product_uom_qty != line.qty_delivered:
                return False
        return True

    def action_done(self):
        res = super(StockPicking, self).action_done()
        hhub = self.env['hhub.config'].search([('company_id', '=', self.env.user.company_id.id)])
        if hhub:
            for picking in self:
                is_all_quantity_done = self.check_done_quantity(picking.sale_id)
                if picking.sale_id and picking.sale_id.is_hhub_order and is_all_quantity_done:
                    request = '''{
                                "Despatches": [
                                {'''
                    for line in picking.move_line_ids:
                        request +='''
                                    "OurOrderReference": %s,
                                    "YourOrderReference": %s,
                                    "LineNumber": %s,
                                    "PackSize": 1,
                                    "PartCode": %s,
                                    "PackType": "EA",
                                    "ShippedQuantity": %s
                                    "ShippedDate": %s
                                    "RemoteShipReference": "sample string 7",
                                    "CarrierName": "FedEx",
                                    "ConsignmentNumber": "sample string 9",
                                    "IsComplete": true
                                    },'''% (picking.id, picking.sale_id.name,line.id,line.product_id.name,
                                                        line.qty_done,picking.date_done)
                    request += ''']
                                    }'''

                    dispatch = HhubConService.post_dispatch_api(picking, request, hhub.dispatch_url, hhub.api_key,
                                                                hhub.secret_key)
        return res