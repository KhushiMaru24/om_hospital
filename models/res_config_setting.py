from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_base_url = fields.Char(string="Web Base URL")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['web_base_url'] = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('web.base.url', self.web_base_url)
