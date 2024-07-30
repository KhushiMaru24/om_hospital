from odoo import models,fields,api

class PharmacyOrder(models.Model):
    _name = 'pharmacy.data'
    _description = 'Pharmacy Order'
    _rec_name = 'product_id'

    patient_id = fields.Many2one('hospital.patient', string="Appointment")
    product_id = fields.Char(string="Medicine")
    price = fields.Float(string="Price")