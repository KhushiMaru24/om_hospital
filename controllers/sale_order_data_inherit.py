import pager
from odoo import http, _
from odoo.http import request



class CreateAppointment(http.Controller):

    @http.route(['/sale/data', '/sale/data/page/<int:page>'], type="http", auth='public', website=True)
    def sale_order_data(self, page=1, **kw):
        sale_orders = request.env['sale.order']
        total_order = sale_orders.search_count([])
        # search_data = sale_orders.search([('id','=',12)]).read()
        # print(search_data)
        # browse_data = sale_orders.browse(12).exists()
        # print(browse_data)
        page_details = request.website.pager(url='/sale/data',
                             total=total_order,
                             page=page,
                             step=5)
        orders = sale_orders.search([], limit=5, offset=page_details['offset'])
        vals = {'sale_orders': orders, 'page_name': 'orders_list_view','pager':page_details}
        return request.render("om_hospital.sale_order", vals)


