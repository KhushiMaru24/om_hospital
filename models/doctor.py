from odoo import models, fields,api
import logging

_logger = logging.getLogger(__name__)
class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Doctor Record'

    name = fields.Char(string="Name", required=True,translate=True)
    login = fields.Char(string="Email", required=True,translate=True)
    password = fields.Char(string="Password", required=True,translate=True)
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id',  string="Pharmacy Lines")

    @api.model
    def create(self, values):
        _logger.info("Starting create method with vals: %s", values)

        user_id = self.env['res.users'].create({
            'name': values.get('name'),
            'login': values.get('login'),
            'password': values.get('password')
        })
        return super(HospitalDoctor,self).create(values)

