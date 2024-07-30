from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit= 'res.users'

    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')