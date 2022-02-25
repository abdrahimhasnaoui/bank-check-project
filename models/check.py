# -*- coding: utf-8 -*-

from random import random
from odoo import models, fields, api
class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    #_order="classment desc,name"
    classment=fields.Char(string='classment',readonly=True,store=True) #,compute="update_partner_classment"
    
    
    
    def update_partner_classment(self):
        #self.classment=self.id
        for partner in self.env['res.partner'].search([]):
            v=self.formule_classe(partner.id)
            #
            #code here
            cls="AB"
            Vals={
                "classment":cls
            }
            partner.write(Vals)
        
        
    def formule_classe(self,partner_id):
        pass



    def get_partner_invoices_count(self,partner_id):
        return self.env['account.invoice'].search_count([('partner_id','=',partner_id)]) 


    def get_partner_dealing_duree_days(self,partner_id):
        # get the first invoice created by that partner
        partner_invoice=self.env['account.invoice'].search([('partner_id','=',partner_id)],order="date_invoice asc",limit=1) 
        if len(partner_invoice)==1:
            return (fields.date.today()-partner_invoice.date_invoice).days
        
        return 0


    def get_invoices_paid_after_dateDue(self,partner_id):  #en retard
        #get all invoices for this partner
        partner_invoices=self.env['account.invoice'].search([
                                                            ('partner_id','=',partner_id), 
                                                            ('state','=','paid')])
        _count=0
        _days=0
        for invoice in partner_invoices:
            #get date of last paiment
            _date=max(invoice.payment_ids.mapped("payment_date"))
            if invoice.date_due < _date:
                _count+=1
                _days+=(_date - invoice.date_due).days

        return {
            "count" : _count,
            "days"  :_days
            }



    def get_invoices_paid_befor_dateDue(self , partner_id) : #avant date d'echeance
        #get all invoices for this partner
        partner_invoices=self.env['account.invoice'].search([
                                                            ('partner_id','=',partner_id), 
                                                            ('state','=','paid')])
        _count=0
        _days=0
        for invoice in partner_invoices:
            #get date of last paiment
            _date=max(invoice.payment_ids.mapped("payment_date"))
            if invoice.date_due > _date:
                _count+=1
                _days+=(invoice.date_due - _date).days

        return {
            "count" : _count,
            "days"  :_days
            }



    def get_invoices_unpaid(self,partner_id):  #invoices not paid
        invoices_list=self.env['account.invoice'].search([
                                                            ('partner_id','=',partner_id), 
                                                            ('date_due','<',fields.date.today()),
                                                            ('state','=','open'),])

        _days=sum([(fields.date.today() - date_due).days for date_due in invoices_list.mapped("date_due")])

        return {
            "count" : len(invoices_list),
            "days"  :_days
            }
        

    
    def get_partner_primes(self,partner_id):
        #get all invoices for this partner
        partner_invoices=self.env['account.invoice'].search([
                                                            ('partner_id','=',partner_id), 
                                                            ('state','=','paid')])
        _count=0
        _primes=0
        for invoice in partner_invoices:
            #get sum amount for all payment
            payment_total=sum(invoice.payment_ids.mapped("amount"))
            if invoice.amount_total_signed < payment_total:
                _count+=1
                _primes=payment_total - invoice.amount_total_signed

        return {
            "count" : _count,
            "primes"  :_primes
            }




class BankCheck(models.Model):
    _name = 'bank.check'
    _rec_name='name_seq'
    _inherit = 'res.partner'

    value = fields.Float(string='Value')
    check_date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
    )
    
    amount_total_outInvoice=fields.Float(string="Total ventes" ,readonly=True)#ventes
    amount_total_inInvoice=fields.Float(string="Total achats" ,readonly=True)#achats
    rest=fields.Float(string="la Difference" ,readonly=True)#ventes - achats
    
    clients_ids = fields.Many2many(
        string='clients',
        comodel_name='res.partner',
    )
    
    ventes_count =fields.Integer(string="ventes" ,compute="get_ventes_count")
    achats_count =fields.Integer(string="ventes" ,compute="get_achats_count")
    # sequence name
    name_seq=fields.Char(string='Check Squence' ,required=True , copy=False ,readonly=True,
                         index=True, default=lambda self:('New'))
    
    
    
    
    @api.model
    def create(self , vals):
        if vals.get('name_seq' , ('New')==('New')):
            vals['name_seq'] =self.env['ir.sequence'].next_by_code('bank.check.sequence') or ('New')
            
        result=super(BankCheck ,self ).create(vals)
        return result
    

       
    @api.onchange('check_date')
    def _calc(self):
        if self.check_date:
            self.calc_amount_total_inInvoice()
            self.calc_amount_total_outInvoice()
            #update field_rest value
            self.rest=self.amount_total_outInvoice-self.amount_total_inInvoice
        
        
        data=""
        for partner in self.env['res.partner'].search([]):
            data+=f"partner_id :{partner.id} , i_count :{self.get_partner_invoices_count(partner.id)} , "
            data+=f"i_duree :{self.get_partner_dealing_duree_days(partner.id) } , "
            data+=f"after :{self.get_invoices_paid_after_dateDue(partner.id)} , "
            data+=f"befor :{self.get_invoices_paid_befor_dateDue(partner.id)} , "
            data+=f"unpaid :{self.get_invoices_unpaid(partner.id)} , "
            data+=f"primes :{self.get_partner_primes(partner.id)} \n"

        return {'warning':{'title' : 'warning' , 'message':f'{data}'}}
            

    
    @api.onchange('clients_ids')
    def _calc2(self):
        if self.check_date:
            self.calc_amount_total_inInvoice()
            self.calc_amount_total_outInvoice()
            #update field_rest value
            self.rest=self.amount_total_outInvoice-self.amount_total_inInvoice
        
        
    @api.onchange('value')
    def _check_value(self):
        if self.value > self.rest:
            return {'warning':{'title' : 'warning' , 'message':'value > Rest'}}
        

            
            
    def calc_amount_total_inInvoice(self):

        f_achats=self.env['account.invoice'].search(
                            [
                              ('type','=','in_invoice'),
                              ('state','=','open'),
                              ('date_due','>=',fields.date.today()),
                              ('date_due','<=',self.check_date),
                            ])
 
        Total=sum(f_achats.mapped("residual_signed"))

        self.amount_total_inInvoice=Total



    def calc_amount_total_outInvoice(self):
        
        #get list of clients selected
        if len(self.clients_ids) == 0 :
            self.amount_total_outInvoice=0.0
            return
        
        f_ventes=self.env['account.invoice'].search(
                            [
                              ('type','=','out_invoice'),
                              ('state','=','open'),
                              ('partner_id','in',self.clients_ids.ids),
                              ('date_due','>=',fields.date.today()),
                              ('date_due','<=',self.check_date),
                            ])
        # Total=0.0
        # for x in f_ventes:
        #     Total+=x.residual_signed
        Total=sum(f_ventes.mapped("residual_signed"))

        self.amount_total_outInvoice=Total
    
    
    
        
    def get_ventes_count(self):
        self.ventes_count=self.env['account.invoice'].search_count([('type','=','out_invoice')])
        
        
    def get_achats_count(self):
        self.achats_count=self.env['account.invoice'].search_count([('type','=','in_invoice')])
        
        
    def open_ventes(self):
        return {
            'name' : ('Ventes'),
            'domain' : [('type','=','out_invoice')],
            'view_type' : 'form',
            'res_model' : 'account.invoice',
            'view_id' : False,
            'view_mode' : 'tree,form',
            'type' : 'ir.actions.act_window',
        }

    def open_achats(self):
        return {
            'name' : ('Achats'),
            'domain' : [('type','=','in_invoice')],
            'view_type' : 'form',
            'res_model' : 'account.invoice',
            'view_id' : False,
            'view_mode' : 'tree,form',
            'type' : 'ir.actions.act_window',
        }