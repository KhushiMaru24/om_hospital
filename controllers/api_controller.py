from odoo import http
from odoo.http import request, Response
import json

class HospitalAPIController(http.Controller):

    @http.route('/api/hospital/patients', type='http', auth='none', methods=['GET'], csrf=False)
    def list_patients(self, **kw):
        patients = request.env['hospital.patient'].sudo().search([])
        patient_data = []
        for patient in patients:
            patient_data.append({
                'id': patient.id,
                'name': patient.name,
                'gender': patient.gender,
                'age': patient.age,
            })
        return Response(json.dumps(patient_data), content_type='application/json')

    @http.route('/api/hospital/appointments', type='http', auth='none', methods=['GET'], csrf=False)
    def list_appointments(self, **kw):
        appointments = request.env['hospital.appointment'].sudo().search([])
        appointment_data = []
        for appointment in appointments:
            appointment_data.append({
                'id': appointment.id,
                'patient_id': appointment.patient_id.name,
                'doctor_id': appointment.doctor_id.name,
                'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d %H:%M:%S'),
                # Add more fields as needed
            })
        return Response(json.dumps(appointment_data), content_type='application/json')
