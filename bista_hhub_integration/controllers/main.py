# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class BistaHhubIntegration(http.Controller):
    @http.route('/bista_hhub_integration', type='json', auth="public")
    def get_json_parameters(self, **kw):
        data = kw
        print ("ddd",data)
        if data.get('OrderContact'):
            OrderContact = data.get('OrderContact')
            CatalogueOrderItems = data.get('CatalogueOrderItems')
            ShipTo = data.get('ShipTo')
            PurchaseOrderNumber = data.get('PurchaseOrders')[0] and data.get('PurchaseOrders')[0].get('PurchaseOrderNumber')
            sale_order_obj = request.env['sale.order']
            sale_order_line_obj = request.env['sale.order.line']
            partner_obj = request.env['res.partner']
            product_obj = request.env['product.product']
            state_obj = request.env['res.country.state']
            country_obj = request.env['res.country']

            state = state_obj.sudo().search([('name','=',ShipTo.get('Region'))])
            country = country_obj.sudo().search([('code','=',ShipTo.get('IsoCountryCode'))])

            sale_order = sale_order_obj.sudo().search([('name', '=', PurchaseOrderNumber)])
            if not sale_order:
                partner = partner_obj.sudo().search([('name','=',OrderContact.get('FullName'))])
                if partner:
                    partner.sudo().write({'email': OrderContact.get('EmailAddress'),'phone': OrderContact.get('TelephoneNumber'),
                                          'street': ShipTo.get('AddressLine1'), 'street2': ShipTo.get('AddressLine2'),
                                          'city': ShipTo.get('Town'), 'state_id': state and state.id or False,
                                          'zip': ShipTo.get('PostCode'), 'country_id': country and country.id or False})
                else:
                    partner = partner_obj.sudo().create({
                        'name': OrderContact.get('FullName'),
                        'email': OrderContact.get('EmailAddress'),
                        'phone': OrderContact.get('TelephoneNumber'),
                        'street': ShipTo.get('AddressLine1'),
                        'street2': ShipTo.get('AddressLine2'),
                        'city': ShipTo.get('Town'),
                        'state_id': state and state.id or False,
                        'zip': ShipTo.get('PostCode'),
                        'country_id': country and country.id or False
                    })
                sale_order = sale_order_obj.sudo().create({'name': PurchaseOrderNumber, 'partner_id': partner.id, 'is_hhub_order': True})

                for line in CatalogueOrderItems:
                    product = product_obj.sudo().search([('default_code','=',line.get('PartCode'))])
                    order_line = sale_order_line_obj.sudo().create({
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'name': line.get('ProductDescription'),
                        'product_uom_qty': line.get('OrderQuantity'),
                        'price_unit': line.get('UnitPrice'),
                        'hhub_line_id': line.get('LineNo')
                    })
            return '200'
        return '404'
