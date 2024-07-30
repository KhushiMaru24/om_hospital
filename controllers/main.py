import logging
from datetime import date, datetime

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


_logger = logging.getLogger(__name__)

class CreateAppointment(http.Controller):

    @http.route('/patient_webform', type="http", auth='public', website=True)
    def patient_webform(self, **kw):
        doctors = request.env['hospital.doctor'].sudo().search([])  # Fetch all doctors, adjust the domain as needed
        return http.request.render("om_hospital.create_patient_website", {
            'docs': doctors,
        })

    @http.route('/create/webpatient', type="http", auth='public', website=True)
    def create_webpatient(self, **kw):
        date_of_birth = kw.get('date_of_birth')
        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        if date_of_birth and date_of_birth > date.today():
            return request.render('om_hospital.create_patient', {
                'warning': {
                    'title': "Invalid Date",
                    'message': "The birth of date must be past date"
                }
            })

        _logger.info('Received form data: %s', kw)
        patient = request.env['hospital.patient'].sudo().create(kw)
        _logger.info('Received form data: %s', patient)
        return request.render("om_hospital.create_appointmentss", {})


