# -*- coding: utf-8 -*-
# from odoo import http


# class Mockbuster(http.Controller):
#     @http.route('/mockbuster/mockbuster', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mockbuster/mockbuster/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mockbuster.listing', {
#             'root': '/mockbuster/mockbuster',
#             'objects': http.request.env['mockbuster.mockbuster'].search([]),
#         })

#     @http.route('/mockbuster/mockbuster/objects/<model("mockbuster.mockbuster"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mockbuster.object', {
#             'object': obj
#         })

