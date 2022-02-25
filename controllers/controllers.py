# -*- coding: utf-8 -*-
from odoo import http

# class BankCheck(http.Controller):
#     @http.route('/bank_check/bank_check/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bank_check/bank_check/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bank_check.listing', {
#             'root': '/bank_check/bank_check',
#             'objects': http.request.env['bank_check.bank_check'].search([]),
#         })

#     @http.route('/bank_check/bank_check/objects/<model("bank_check.bank_check"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bank_check.object', {
#             'object': obj
#         })