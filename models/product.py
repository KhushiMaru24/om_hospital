from odoo import models, fields, api
from itertools import groupby
from operator import itemgetter
from datetime import date


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_product_templates(self):
        # Fetch product templates with their base list price
        templates = self.search_read([], [])
        return templates

    @api.model
    def get_product_info_pos(self, product_variant_ids, price, quantity, config_id):
        if not product_variant_ids:
            return []

        product_variants = self.env['product.product'].browse(product_variant_ids)
        config_param = self.env['ir.config_parameter'].sudo().get_param('pos_default_location_id')
        if not config_param:
            raise ValueError("POS default location parameter not set")

        location = self.env['stock.location'].browse(int(config_param))
        if not location:
            raise ValueError("Configured stock location not found")

        warehouse_list = []
        for product_variant in product_variants:
            qty_available = self.env['stock.quant'].search([
                ('product_id', '=', product_variant.id),
                ('location_id', '=', location.id)
            ]).quantity

            warehouse_list.append({
                'product_variant_id': product_variant.id,
                'product_tmpl_id': product_variant.product_tmpl_id.id,
                'qty_available': qty_available,
            })

        return warehouse_list