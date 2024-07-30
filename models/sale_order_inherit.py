from odoo import models, api, fields

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    _order = "id asc"