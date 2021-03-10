# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class run_time_exec(models.TransientModel):
    _name = 'run.time.exec'
    _description = 'Run Time Execution'

    data = fields.Binary('File')
    name = fields.Char('Filename')
    code_to_execute = fields.Text('Code')

    @api.multi
    
    def execute_code(self):
#import logging
#_logger = logging.getLogger(__name__)
#i = 1
#search_product_ids = self.env['product.product'].search([('attribute_value_ids.attribute_id','=', 1)])
#_logger.info("--len (search_product_ids) %s" % len(search_product_ids))
#for each_prod in search_product_ids:
#    attribute_value_name = each_prod.attribute_value_ids[0].name
#    each_prod.default_code = attribute_value_name
#    i = 1
#import csv
#from tempfile import TemporaryFile
#import base64
#import logging
#_logger = logging.getLogger(__name__)
#fileobj = TemporaryFile('w+')
#file_data = base64.decodebytes(self.data).decode("utf-8")
#fileobj.write(file_data)
#fileobj.seek(0)
#reader = csv.reader(fileobj, delimiter=',')
#attribute_id = 1
#attribute_value_obj = self.env['product.attribute.value']
#product_data = {}
#for count, row in enumerate(reader):
#        if count > 0:
#            parent_prod_name = str(row[0]).strip()
#            variant_name = str(row[1]).strip()
#            cr = self._cr
#            cr.execute("select id from product_template where name ilike '%s'" % (parent_prod_name))
#            product_tmpl_id = list(filter(None, map(lambda x: x, cr.fetchall())))
#            if product_tmpl_id:
#                    cr.execute("select id from product_attribute_value where name ilike '%s' and attribute_id=%s" % (variant_name, attribute_id))
#            attr_value_exists = list(filter(None, map(lambda x: x, cr.fetchall())))
#            if attr_value_exists:
#                if product_tmpl_id[0] not in product_data:
#                    product_data[product_tmpl_id[0]]  = attr_value_exists
#                else:
#                    existing_value_ids = product_data.get(product_tmpl_id[0])
#                    product_data[product_tmpl_id[0]] = attr_value_exists + existing_value_ids
#
#_logger.info("--product_data %s" % product_data)
#if product_data:
#    tmpl_obj = self.env['product.template']
#    for key,value in product_data.items():
#        tmpl_brw = tmpl_obj.browse(key)			
#        vals = {'attribute_line_ids': [(0,0,{'attribute_id': 1, 'value_ids': [(6, 0, value)]})]}
#        tmpl_brw.write(vals)
#    import csv
#from tempfile import TemporaryFile
#import base64
#import logging
#_logger = logging.getLogger(__name__)
#fileobj = TemporaryFile('w+')
#file_data = base64.decodebytes(self.data).decode("utf-8")
#fileobj.write(file_data)
#fileobj.seek(0)
#reader = csv.reader(fileobj, delimiter=',')
#attribute_id = 1
#attribute_value_obj = self.env['product.attribute.value']
#for count, row in enumerate(reader):
#  if count > 0:
#    variant_name = str(row[0]).strip()
#    cr = self._cr
#    cr.execute("select id from product_attribute_value where name ilike '%s' and attribute_id=%s" % (variant_name, attribute_id))
#    attr_value_exists = list(filter(None, map(lambda x: x, cr.fetchall())))
#    if not attr_value_exists:
#      attribute_value_obj.create({'name': variant_name, 'attribute_id': attribute_id})
#    _logger.info("---curr_row value %s" % count)
        try:
            exec(self.code_to_execute)
        except Exception as e:
            raise UserError(_('Error %s' % (str(e))))
