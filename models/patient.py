from odoo import api, fields, models, _
from datetime import date
# from odoo17.odoo.exceptions import ValidationError

class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ["mail.thread","mail.activity.mixin"]
    _description = "Hospital Patient"
    _rec_name = 'name'
    _order = "id desc"

    name = fields.Char(string='Name', tracking=True,translate=True)
    ref = fields.Char(string='Reference')
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', tracking=True)
    gender = fields.Selection([('male','Male'),('female','Female')], string='Gender', tracking=True)
    # active = fields.Boolean(string="Active")
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    image = fields.Image(string="Image")
    # tag_ids = fields.Many2many('patient.tag', string="Tags")
    appointment_count = fields.Integer(string="Appointment Count", compute='_compute_appointment_count', stored=True)
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointments")
    is_birthday = fields.Boolean(string="Birthday ?", compute="_compute_is_birthday")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")
    # data = fields.Many2one('pharmacy.sale.order.data', string="Medicine")
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    prescription = fields.Html(related='appointment_ids.prescription')
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', compute='_compute_pharmacy_ids', string="Pharmacy Lines")

    @api.depends('appointment_ids.pharmacy_line_ids')
    def _compute_pharmacy_ids(self):
        for rec in self:
            rec.pharmacy_line_ids = [(6,0, rec.appointment_ids.mapped('pharmacy_line_ids').ids)]


    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['hospital.appointment'].search_count([('patient_id','=',rec.id)])

    # @api.constrains('date_of_birth')
    # def _check_date_of_birth(self):
    #     for rec in self:
    #         if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
    #             raise ValidationError(_("The enter date not accepted"))

    # @api.model
    # def create(self, vals):
    #     print("ho gys.")
    #     vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
    #     return super(HospitalPatient, self).create(vals)
    #
    # def write(self, vals):
    #     print("write override")
    #     if not self.ref:
    #         vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
    #     return super(HospitalPatient, self).write(vals)

    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
               rec.age = 0

    def name_get(self):
        patient_list = []
        for record in self:
            name = record.ref +" "+ record.name
            patient_list.append(record.id, name)
        return patient_list

    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        for rec in self:
            is_birthday = False
            if rec.date_of_birth:
                today = date.today()
                if today.day == rec.date_of_birth.day and today.month == rec.date_of_birth.month:
                    is_birthday = True
            rec.is_birthday = is_birthday

    def action_view_appointment(self):
        return{
            'name': _('Appointment'),
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form,calendar,activity',
            'context': {'default_patient_id':self.id},
            'domain':[('patient_id','=',self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window'
        }

    @api.model
    def create_patient(self, values):

        user_id = self.env['hospital.patient'].create({
            'name': values.get('name'),
            'age': values.get('age'),
            'gender': values.get('gender')
        })
        return super(HospitalPatient, self).create(values)







