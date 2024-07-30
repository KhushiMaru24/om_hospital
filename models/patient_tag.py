from odoo import api, fields, models, _

class HospitalPatient(models.Model):
    _name = "patient.tag"
    _description = "Patient Tag"
    _order = 'sequence,id'

    name = fields.Char(string="Name", required=True, trim=False,translate=True)
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color")
    color_2 = fields.Char(string="Color 2")
    sequence = fields.Integer(string="Sequence", default=10)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique.')
    ]