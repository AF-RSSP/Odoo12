# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ProductDimensionsVolume(models.Model):
    _inherit = 'product.template'

    length = fields.Char(string="Length")
    width = fields.Char(string="Width")
    height = fields.Char(string="Height")

    @api.depends('length', 'width', 'height','product_variant_ids', 'product_variant_ids.volume')
    def _compute_volume(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.volume = template.product_variant_ids.volume
        for template in (self - unique_variants):
            template.volume = 0.0
        for template in self:
            template.volume = float(template.length if template.length else 0) * float(template.width if template.width else 0) * float(template.height if template.height else 0)




