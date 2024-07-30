from odoo import models, fields, api

class HospitalPatientCreateWizard(models.TransientModel):
    _name = 'hospital.patient.create.wizard'
    _description = 'Create Patient Wizard'

    name = fields.Char('Patient Name', required=True)

    def create_patient(self):
        patient_vals = {
            'name': self.name,
        }
        new_patient = self.env['hospital.patient'].sudo().create(patient_vals)
        return new_patient
