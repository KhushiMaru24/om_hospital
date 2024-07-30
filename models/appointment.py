from datetime import date, timedelta
from odoo import api, fields, models, _
#from odoo17.odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ["mail.thread","mail.activity.mixin"]
    _description = "Hospital Patient"
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('hospital.patient', string="Patient")
    gender = fields.Selection(related="patient_id.gender")
    # sale_order_id = fields.Many2one('pharmacy.sale.order.data', string="Sale Order")
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    patient = fields.One2many('hospital.patient','appointment_id')
    appointment_time = fields.Datetime(String="Booking Datetime", default=fields.Datetime.now)
    appointment_date= fields.Date(String="Booking Date", default=fields.Date.context_today)
    ref = fields.Char(string='Reference', help="Reference of the patient")
    prescription = fields.Html(string='Prescription')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string="Priority")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], default="draft", string="Status",required=True)
    doctor = fields.Many2one('res.users', string="Doctor")
    data = fields.Many2one('sale.order', string="Medicine")
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines','appointment_id', string="Pharmacy Lines")
    hide_sales_price = fields.Boolean(string="Hide Sales Price")
    progress = fields.Integer(string="Progress", compute="_compute_progress")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    sale_order_count = fields.Integer(string="Sale Order Count", compute='_compute_sale_order_count', stored=True)
    sale = fields.One2many('sale.order','ref', string="Sale_order")
    appointment = fields.Integer(related='sale.appointment')
    reference = fields.Char(string="Order Reference", required=True, copy=False, readonly=True,index='trigram',default=lambda self: _('New'))
    app = fields.Boolean(compute='_compute_app')

    @api.model
    def send_reminder_emails(self):
        today = fields.Datetime.now()
        tomorrow = today + timedelta(days=1)
        appointments = self.search([('appointment_date', '>=', today),
                                    ('appointment_date', '<', tomorrow)])
        for appointment in appointments:
            patient = appointment.patient_id
            # Your logic to send email
            _logger.info(f"Reminder email sent to {patient.name} for appointment on {appointment.appointment_date}")

    @api.depends('sale')
    def _compute_app(self):
        exist = self.env['sale.order'].search([('appo', '=', self.reference)], limit=1)
        if exist:
            self.app = True
        else:
            self.app = False

    @api.depends('appointment_id.pharmacy_line_ids')
    def _compute_pharmacy_ids(self):
        for rec in self:
            rec.pharmacy_line_ids = [(6, 0, rec.appointment_id.mapped('pharmacy_line_ids').ids)]

    @api.depends('sale')
    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = self.env['sale.order'].search_count([('appo', '=', self.reference)])

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def create(self, vals):
        if vals.get('refrence',_('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        return super(HospitalAppointment, self).create(vals)

    @api.onchange('appointment_date')
    def _onchange_appointment_date(self):
        if self.appointment_date:
            try:
                   appointment_date = fields.Date.from_string(self.appointment_date)
            except ValueError:
                self.appointment_date = False
                return {
                    'warning': {
                        'title': "Invalid Date",
                        'message': "The appointment date is required"
                    }
                }
            if appointment_date < date.today():
                self.appointment_date = False
                return {
                    'warning': {
                        'title': "Invalid Date",
                        'message': "The appointment date must be today or future date"
                    }
                }

    # @api.constrains('appointment_date')
    # def _check_appointment_date(self):
    #     for rec in self:
    #         if not rec.appointment_date:
    #             raise ValidationError(_("The appointment date is required"))
    #         try:
    #             appointment_date = fields.Date.from_string(rec.appointment_date)
    #         except ValueError:
    #             raise ValidationError(_("The appointment date is not valid"))
    #         if appointment_date<date.today():
    #             raise ValidationError(_("The appointment date must be today or future date"))

    def action_test(self):
        msg = "Display Notification"
        action = self.env.ref('om_hospital.action_hospital_patient')
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'message': msg,
        #         'type': 'success',
        #         'links': [{
        #             'label': self.patient_id.name,
        #             'url': f'#action={action.id}&id={self.patient_id.id}&model=hospital.patient'
        #         }],
        #         'sticky': True,
        #     }
        # }
        return{
           'effect': {
               'fadeout': 'slow',
               'message': 'Click Successful',
               'type': 'rainbow_man'
           }
        }
        # return {
        #     'type':'ir.actions.act_url',
        #     'target': 'self',
        #     'url': 'https://www.odoo.com'
        # }

    def action_in_consultation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_consultation'

    def sale_order_open(self):
        return{
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'view_mode': 'list,form,calendar,activity',
            'domain':[('appo', '=', self.reference)],
            'target': 'current',
            'type': 'ir.actions.act_window'
        }

    def action_done(self):
        for rec in self:
            if rec.state == 'in_consultation':
                rec.state = 'done'

        existing_sale_order = self.env['sale.order'].search([('appo', '=', self.reference)], limit=1)

        if existing_sale_order:
            print("already present")
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pharmacy Sale Order',
                'res_model': 'sale.order',
                'res_id': existing_sale_order.id,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }
        patient = self.env['hospital.patient'].browse(self.patient_id.id).name
        customer = self.env['res.partner'].create({
            'name': patient,
        })
        print(self.reference)
        app = self.reference
        sale_order = {
            'partner_id': customer.id,
            'appo': app,
            'order_line': [],
        }
        print(sale_order)
        pharmacy_lines = self.env['appointment.pharmacy.lines'].search([('appointment_id', '=', self.id)])
        _logger.info(f"Pharmacy Lines for Appointment {self.id}: {pharmacy_lines.ids}")
        order_lines = []
        for line in pharmacy_lines:
            medicine = self.env['appointment.pharmacy.lines'].browse(line.id).product.product_id
            prices = self.env['appointment.pharmacy.lines'].browse(line.id).prices
            product = self.env['product.product'].create({
                'name': medicine,
                'list_price': prices,
                'type': 'consu',
            })
            order_line_vals = {
                'product_id': product.id,
                'product_uom_qty': line.qty,
                'price_unit': product.list_price,
            }
            sale_order['order_line'].append((0, 0, order_line_vals))

        sale_orders = self.env['sale.order'].create(sale_order)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Pharmacy Sale Order',
            'res_model': 'sale.order',
            'res_id': sale_orders.id,
            'view_mode': 'form',
            'view_type': 'tree,form',
            'view_id': False,
            'target': 'current',
        }

    def action_cancel(self):
        for rec in self:
            if rec.state == 'in_consultation':
                rec.state = 'cancel'

    def action_share_whatsapp(self):
        # if not self.patient_id.phone:
        #     raise ValidationError(_("Patient does not have phone."))
        msg = 'Hi *%s*, your appointment date is %s' % (self.patient_id.name, self.appointment_date)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.phone, msg)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = 25
            elif rec.state == 'in_consultation':
                progress = 50
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress

    def action_send_email(self):
        template = self.env.ref('om_hospital.patient_card_email_template')
        for rec in self:
            if rec.patient_id.email:
                template.send_mail(rec.id)

    @api.model
    def fetch_data(self):
        patient_count = self.env['hospital.patient'].search_count([])
        appointment_count = self.env['hospital.appointment'].search_count([])
        patients = self.env['hospital.patient'].search([])
        pharmacy_data = self.env['appointment.pharmacy.lines'].search([])
        patient_data = []
        pharmy = []
        for patient in patients:
            appointment_c = self.env['hospital.appointment'].search_count([('patient_id.name', '=', patient.name)])
            appointments = self.env['hospital.appointment'].search([('patient_id.name', '=', patient.name)])

            # Accumulate pharmacy data related to these appointments
            for appointment in appointments:
                pharmacy_lines = self.env['appointment.pharmacy.lines'].search(
                    [('appointment_id', '=', appointment.id)])

                for pharmacy_record in pharmacy_lines:
                    product_name = pharmacy_record.product.product_id
                    quantity = pharmacy_record.qty

                    # Append pharmacy data for each product
                    pharmy.append({
                        'product_name': product_name,
                        'quantity_added': quantity,
                    })
            patient_data.append({
                'patient_name': patient.name,
                'appointment_count': appointment_c,
            })
        product_qty_map = {}

        # Aggregate quantities per product
        for pharmacy_record in pharmy:
            product_name = pharmacy_record['product_name']
            quantity = pharmacy_record['quantity_added']

            if product_name in product_qty_map:
                product_qty_map[product_name] += quantity
            else:
                product_qty_map[product_name] = quantity

        # Prepare data in required format
        product_data = []
        for product_name, quantity_added in product_qty_map.items():
            product_data.append({
                'product_name': product_name,
                'quantity_added': quantity_added,
            })


        return {
            'patient_count': patient_count,
            'appointment_count': appointment_count,
            'pharmacy_data': product_data,
            'patient_data': patient_data,
        }


class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    product = fields.Many2one('pharmacy.data', string="Medicine")
    prices = fields.Float(related="product.price")
    qty = fields.Integer(string="Quantity",default='1')
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    patient_id = fields.Many2one('hospital.patient', string="Appointment")
    currency_id = fields.Many2one(related="appointment_id.currency_id")
    price_subtotal = fields.Monetary(string="Subtotal", compute="_compute_price_subtotal")
    total_price = fields.Float(string="Total Price")
    # data = fields.Many2one('pharmacy.sale.order.data', string="Medicine")


    @api.depends('prices', 'qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.prices * rec.qty

