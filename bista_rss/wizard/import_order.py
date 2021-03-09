##############################################################################
#
#    Bista Solutions
#    Copyright (C) 2019 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64
import xlrd
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta


class ImportOrder(models.TransientModel):
    _name = "import.order"
    _description = "Import Order"

    xls_file = fields.Binary(string="Attach a file here!", required=True, )
    filename = fields.Char('Filename')
    not_imported_order = fields.Text("Following Orders are not Imported/Updated")

    @api.constrains('xls_file', 'filename')
    def file_check(self):
        if self.filename and not self.filename.lower().strip().endswith('.xls'):
            raise UserError(_("Selected file is not .xls, Please select .xls file"))

    def XLSDictReader(self, sheet):
        headers = dict((i, sheet.cell_value(0, i)) for i in range(sheet.ncols))
        return (dict((headers[j], sheet.cell_value(i, j)) for j in headers) for i in range(1, sheet.nrows))

    def check_or_create_cust_tag(self, customer_tag_ids, tag_obj):
        tag_id = False
        self._cr.execute("select id from res_partner_category where name ilike '%s'" % customer_tag_ids)
        odoo_tag_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))
        if odoo_tag_id:
            tag_id = odoo_tag_id[0]
        else:
            final_customer_tag = [{'name': customer_tag_ids}]
            new_tag_id = tag_obj.create(final_customer_tag)
            tag_id = new_tag_id.id
        return tag_id

    def check_or_create_partner_shipping(self, val, customer_billing_full_name, partner_obj, tag_id):
        customer_billing_street = val.get('Billing Address 1')
        customer_billing_street1 = val.get('Billing Address 2')
        customer_billing_city = val.get('Billing City')
        customer_email = val.get('Email')
        customer_billing_zip = val.get('Billing Zip/Postal Code')
        customer_billing_state = val.get('Billing State/Province')
        customer_billing_country = val.get('Billing Country Full Name')
        customer_billing_phone = val.get('Billing Phone')
        customer_billing_mobile = val.get('Billing Cell Phone')
        odoo_country_id = odoo_state_id = False
        self._cr.execute("select id from res_country where name ilike '%s'" % customer_billing_country)
        odoo_country_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))

        if odoo_country_id:
            self._cr.execute("select id from res_country_state where code='%s' and country_id=%s" % (
                customer_billing_state, odoo_country_id[0]))
            odoo_state_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))
        final_customer_dict = [{'name': customer_billing_full_name or False,
                                'street': customer_billing_street or False,
                                'street2': customer_billing_street1 or False,
                                'city': customer_billing_city or False,
                                'zip': customer_billing_zip or False,
                                'email': customer_email or False,
                                'state_id': odoo_state_id[0] if odoo_state_id else False,
                                'country_id': odoo_country_id[0] if odoo_country_id else False,
                                'phone': customer_billing_phone or False,
                                'mobile': customer_billing_mobile or False,
                                'category_id': [(6, 0, [tag_id])] if tag_id else [],
                                }]
        partner_id = partner_obj.create(final_customer_dict)
        partner_id = partner_id.id
        # Search shipping partner
        customer_shipping_full_name = val.get('Shipping First Name') + ' ' + val.get(
            'Shipping Last Name')
        customer_shipping_country = val.get('Shipping Country Full Name')
        customer_shipping_state = val.get('Shipping State/Province')
        odoo_shipping_country_id = False
        self._cr.execute("select id from res_country where name ilike '%s'" % customer_shipping_country)
        odoo_shipping_country_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))

        if odoo_shipping_country_id:
            self._cr.execute("select id from res_country_state where code='%s' and country_id=%s" % (
                customer_shipping_state, odoo_shipping_country_id[0]))
            odoo_state_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))
            final_shipping_dict = [{'parent_id': partner_id,
                                    'type': 'delivery',
                                    'name': customer_shipping_full_name or False,
                                    'street': val.get('Shipping Address 1') or False,
                                    'street2': val.get('Shipping Address 2') or False,
                                    'city': val.get('Shipping City') or False,
                                    'email': customer_email or False,
                                    'state_id': odoo_state_id[0] if odoo_state_id else False,
                                    'country_id': odoo_shipping_country_id[
                                        0] if odoo_shipping_country_id else False,
                                    'phone': val.get('Shipping Phone') or False,
                                    'mobile': val.get('Shipping Cell Phone') or False,
                                    }]
            shipping_partner_id = partner_obj.create(final_shipping_dict)
            shipping_partner_id = shipping_partner_id.id
            return partner_id, shipping_partner_id

    def check_if_ship_add_correct(self, val, partner_id, partner_obj):
        customer_shipping_full_name = val.get('Shipping First Name') + ' ' + val.get(
            'Shipping Last Name')
        customer_email = val.get('Email')
        street = val.get('Shipping Address 1')
        city = val.get('Shipping City')
        customer_shipping_country = val.get('Shipping Country Full Name')
        customer_shipping_state = val.get('Shipping State/Province')
        self._cr.execute("select id from res_country where name ilike '%s'" % customer_shipping_country)
        odoo_shipping_country_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))
        odoo_state_id = ''

        if odoo_shipping_country_id:
            self._cr.execute("select id from res_country_state where code='%s' and country_id=%s" % (
                customer_shipping_state, odoo_shipping_country_id[0]))
            odoo_state_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))
        # search partner
        delivery = 'delivery'
        self._cr.execute("select id from res_partner where type='%s' and street='%s' and city='%s' and "
                         "state_id=%s and country_id=%s and parent_id =%s" % (
                             delivery, street, city, odoo_state_id[0], odoo_shipping_country_id[0],
                             partner_id))
        odoo_partner_id = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))

        if odoo_partner_id:
            shipping_partner_id = odoo_partner_id[0]

        else:
            final_shipping_dict = [{'parent_id': partner_id,
                                    'type': 'delivery',
                                    'name': customer_shipping_full_name or False,
                                    'street': street or False,
                                    'street2': val.get('Shipping Address 2') or False,
                                    'city': city or False,
                                    'email': customer_email or False,
                                    'state_id': odoo_state_id[0] if odoo_state_id else False,
                                    'country_id': odoo_shipping_country_id[
                                        0] if odoo_shipping_country_id else False,
                                    'phone': val.get('Shipping Phone') or False,
                                    'mobile': val.get('Shipping Cell Phone') or False,
                                    }]
            shipping_partner_id = partner_obj.create(final_shipping_dict)
            shipping_partner_id = shipping_partner_id.id
        return shipping_partner_id

    def import_order(self):
        not_imported_order = ''
        form_view_id = (self.env.ref('sale.view_order_form').id, 'form')
        tree_view_id = (self.env.ref('sale.view_quotation_tree').id, 'tree')
        so_ids_list = []
        so_line_data = {}
        user_id = self.env.user.id
        current_time = datetime.utcnow().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if self.xls_file:
            content = base64.b64decode(self.xls_file)
            book = xlrd.open_workbook(file_contents=content)
            sheet = book.sheet_by_index(0)
            xl_dict = self.XLSDictReader(sheet)
            partner_obj = self.env['res.partner']
            users_obj = self.env['res.users']
            sale_order_obj = self.env['sale.order']
            sale_order_line_obj = self.env['sale.order.line']
            product_obj = self.env['product.product']
            tax_obj = self.env['account.tax']
            tag_obj = self.env['res.partner.category']
            count = 0
            expected_column_list = ['Order Number', 'Billing First Name', 'Billing Last Name', 'Type', 'Sku', 'Desc',
                                    'Quantity', 'Price']
            cr = self._cr
            for val in xl_dict:
                _logger.info('count %s', count)
                if count == 0:
                    val_keys = val.keys()
                    unmatched_header = list(set(expected_column_list) - set(val_keys))
                    if unmatched_header:
                        unmatched_header = ', '.join(unmatched_header)
                        expected_header = ', '.join(expected_column_list)
                        raise UserError(_(
                            "Uploaded File Headers are not correct.\n Expected headers are %s.\n Mistmatch headers "
                            "are %s.") % (expected_header, unmatched_header))
                count += 1
                if val.get('Type') == 'Summary':
                    customer_billing_first_name = customer_billing_last_name = customer_billing_state = ''
                    customer_billing_first_name = val.get('Billing First Name')
                    customer_billing_last_name = val.get('Billing Last Name')
                    customer_billing_full_name = customer_billing_first_name + ' ' + customer_billing_last_name
                    partner_id = partner_obj.search(
                        [('name', '=', customer_billing_full_name), ('type', '=', 'contact'),
                         ('parent_id', '=', False)])
                    customer_tag_ids = val.get('Tag')
                    tag_id = False
                    if customer_tag_ids:
                        tag_id = self.check_or_create_cust_tag(customer_tag_ids, tag_obj)
                    if not partner_id:
                        partner_id, shipping_partner_id = self.check_or_create_partner_shipping(val,
                                                                                                customer_billing_full_name,
                                                                                                partner_obj, tag_id)

                    else:
                        if isinstance(partner_id, int):
                            shipping_partner_id = self.check_if_ship_add_correct(val, partner_id, partner_obj)
                        else:
                            shipping_partner_id = self.check_if_ship_add_correct(val, partner_id.id, partner_obj)

                        partner_id = partner_id[0]
                        if tag_id and not partner_id.category_id:
                            partner_id.write({'category_id': [(6, 0, [tag_id])] or []})
                        partner_id = partner_id[0].id
                    date = val.get('Order Date')
                    f = date.split("/")
                    so_date_order = "20" + f[2] + "-" + f[0].rjust(2, "0") + "-" + f[1].rjust(2, "0") + " 05:30:00"
                    # sale_order parameter
                    so_name = val.get('Order Number', '')
                    so_name = str(so_name).replace('.0', '')
                    if val.get('Status', '') == "Pending":
                        val['Status'] = 'pending'
                    # check sale order is already created
                    cr.execute("select id, state from sale_order where name='%s'" % (so_name))
                    so_id = list(filter(None, map(lambda x: x, cr.fetchall())))
                    if so_id and (so_id[0][1] == 'draft'):
                        so_id = so_id[0][0]
                        cr.execute("delete from sale_order_line where order_id =%s" % so_id)
                        final_so_dict = {
                            'partner_id': partner_id or False,
                            'partner_shipping_id': shipping_partner_id or partner_id,
                            'date_order': so_date_order or False,
                            'rss_state': val.get('Status', ''),
                            'user_id': user_id or False,
                            'client_order_ref': val.get('Cust Ref'),
                            'note': val.get('Order Type', ''),
                        }
                        so_id_brw = sale_order_obj.sudo().browse(so_id)
                        so_id_brw.write(final_so_dict)
                        so_ids_list.append(so_id)
                        if so_id not in so_line_data:
                            so_line_data[so_id] = {'amount_total': 0.0, 'line_items': []}
                    elif so_id and (so_id[0][1] != 'draft'):
                        not_imported_order += 'Row ' + str(
                            count + 1) + ' SO %s is not imported because SO is in other than Draft state. \n' % (
                                                  so_name)
                        pass
                    else:
                        final_so_dict = {
                            'name': so_name or False,
                            'partner_id': partner_id or False,
                            'partner_shipping_id': shipping_partner_id or partner_id,
                            'date_order': so_date_order or False,
                            'rss_state': val.get('Status', ''),
                            'user_id': user_id or False,
                            'client_order_ref': val.get('Cust Ref'),
                            'note': val.get('Order Type', ''),
                        }
                        so_id = sale_order_obj.create(final_so_dict)
                        so_ids_list.append(so_id.id)
                        if so_id.id not in so_line_data:
                            so_line_data[so_id.id] = {'amount_total': 0.0, 'line_items': []}
                elif val.get('Type') == 'Item':
                    so_name = sol_product_internal_ref = ''
                    so_name = val.get('Order Number')
                    so_name = str(so_name).replace('.0', '')
                    # sale_order_line parameter
                    sol_product_internal_ref = val.get('Sku', '')
                    if sol_product_internal_ref:
                        sol_product_description_name = val.get('Desc', '')
                        sol_product_qty = val.get('Quantity', 0.0)
                        sol_discount = val.get('Discount-Percentage', 0.0)
                        sol_price = val.get('Price', 0.0)
                        cr.execute("select id, state from sale_order where name='%s'" % (so_name))
                        so_id = list(filter(None, map(lambda x: x, cr.fetchall())))
                        cr.execute("""select id from product_product where default_code ='%s'""" % (sol_product_internal_ref))
                        product_id = list(filter(None, map(lambda x: x[0], cr.fetchall())))
                        if product_id:
                            if so_id and (so_id[0][1] == 'draft'):
                                so_id = so_id[0][0]
                                price_subtotal = sol_product_qty * sol_price
                                if so_id in so_line_data:
                                    so_line_data[so_id]['amount_total'] += price_subtotal
                                    so_line_data[so_id]['line_items'].extend([(current_time,current_time,user_id,user_id,so_id,sol_product_description_name,product_id[0],1,sol_product_qty, sol_price,price_subtotal,sol_discount or 0.0,1,'draft')])
                            elif not so_id:
                                not_imported_order += 'Row ' + str(
                                    count + 1) + 'SO %s is not imported because SO is not ' \
                                                 'found. \n' % (so_name)
                            else:
                                not_imported_order += 'Row ' + str(
                                    count + 1) + 'SO %s is not imported because SO is in other ' \
                                                 'than Draft state. \n' % (so_name)
                        else:
                            not_imported_order += 'Row ' + str(count + 1) + ': %s : Product SKU ::  %s, Not Found ' \
                                                                            'In System. \n' % (so_name,
                                                                                               sol_product_internal_ref)
                else:
                    pass
        if so_line_data:
            for key,value in so_line_data.items():
                so_brw = sale_order_obj.browse(key)
                amount_total = value.get('amount_total', 0.0)
                line_items = value.get('line_items', [])
                stmt = "insert into sale_order_line (create_date,write_date,create_uid,write_uid,order_id,name,product_id,product_uom,product_uom_qty,price_unit,price_subtotal,discount,customer_lead,state) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id"
                self._cr.executemany(stmt, line_items)
                self._cr.commit()
                self._cr.execute("update sale_order set amount_untaxed=%s, amount_total=%s where id=%s" % (amount_total, amount_total, key))

        if not_imported_order:
            self.write({'not_imported_order': not_imported_order})
            return {
                'name': _('Import Orders'),
                'domain': [('id', '=', self.id)],
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.order',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'sale_order_ids': so_ids_list
            }
        else:
            return {
                'name': _('Imported Orders'),
                'domain': [('id', 'in', so_ids_list)],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'views': [tree_view_id, form_view_id],
                'view_id': [form_view_id],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }
