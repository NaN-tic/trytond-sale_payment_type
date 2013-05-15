#This file is part of sale_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['Sale']
__metaclass__ = PoolMeta

_STATES = {
    'readonly': Eval('state') != 'draft',
}
_DEPENDS = ['state']


class Sale:
    'Sale'
    __name__ = 'sale.sale'

    payment_type = fields.Many2One('account.payment.type',
        'Payment Type', states=_STATES, depends=_DEPENDS,
        domain=[('kind','=','receivable')])

    @classmethod
    def default_payment_type(cls):
        PaymentType = Pool().get('account.payment.type')
        payment_types = PaymentType.search(cls.payment_type.domain)
        if len(payment_types) == 1:
            return payment_types[0].id

    def on_change_party(self):
        changes = super(Sale, self).on_change_party()
        if self.party and self.party.customer_payment_type:
            changes['payment_type'] = self.party.customer_payment_type.id
        return changes

    def _get_invoice_sale(self, invoice_type):
        invoice = super(Sale, self)._get_invoice_sale(invoice_type)
        if self.payment_type:
            if invoice_type == 'out_credit_note':
                invoice.payment_type = self.party.supplier_payment_type
            else
                invoice.payment_type = self.payment_type
        return invoice
