from odoo import models

class PatientCardXlsx(models.AbstractModel):
    _name = 'report.om_hospital.report_patient_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter'})
        sheet = workbook.add_worksheet('Patient Card')
        # sheet.right_to_left()
        # sheet.set_column(3,3,50)
        sheet.write(0,0, 'Name', format1)
        sheet.write(0,1, lines.name, format2)
        sheet.write(1,0, 'Age', format1)
        sheet.write(1, 1, lines.age, format2)
