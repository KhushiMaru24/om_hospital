from odoo import models, fields, api

class FavoritePatient(models.Model):
    _name = 'hospital.favorite.patient'
    _description = 'Favorite Patient'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)