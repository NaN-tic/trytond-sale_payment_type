#This file is part of sale_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['PaymentType', 'Sale']

_STATES = {
    'readonly': Eval('state') != 'draft',
}
_DEPENDS = ['state']


class PaymentType:
    __metaclass__ = PoolMeta
    __name__ = 'account.payment.type'

    @classmethod
    def __setup__(cls):
        super(PaymentType, cls).__setup__()
        cls._check_modify_related_models.add(('sale.sale', 'payment_type'))


class Sale:
    __metaclass__ = PoolMeta
    __name__ = 'sale.sale'
    payment_type = fields.Many2One('account.payment.type', 'Payment Type',
        domain=[('kind', '=', 'receivable')], states=_STATES, depends=_DEPENDS)

    @classmethod
    def default_payment_type(cls):
        PaymentType = Pool().get('account.payment.type')
        payment_types = PaymentType.search(cls.payment_type.domain)
        if len(payment_types) == 1:
            return payment_types[0].id

    @fields.depends('party')
    def on_change_party(self):
        self.payment_type = None
        super(Sale, self).on_change_party()
        if self.party and self.party.customer_payment_type:
            self.payment_type = self.party.customer_payment_type

    def _get_invoice_sale(self):
        invoice = super(Sale, self)._get_invoice_sale()
        if self.payment_type:
            if invoice.type == 'out' and self.total_amount < 0.0:
                invoice.payment_type = self.party.supplier_payment_type
            else:
                invoice.payment_type = self.payment_type
        return invoice
