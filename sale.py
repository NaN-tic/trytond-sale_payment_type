# This file is part of sale_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['PaymentType', 'Sale', 'Opportunity']

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
        states=_STATES, depends=_DEPENDS,
        domain=[
            ('kind', 'in', ['both', 'receivable']),
            ])

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

    def _get_grouped_invoice_domain(self, invoice):
        invoice_domain = super(Sale, self)._get_grouped_invoice_domain(invoice)
        invoice_domain.append(
            ('payment_type', '=', self._get_invoice_payment_type(invoice)))
        return invoice_domain

    def _get_invoice_sale(self):
        invoice = super(Sale, self)._get_invoice_sale()
        invoice.payment_type = self._get_invoice_payment_type(invoice)
        return invoice

    def _get_invoice_payment_type(self, invoice):
        if getattr(invoice, 'payment_type', False):
            return invoice.payment_type
        if self.payment_type:
            if self.payment_type.kind != 'both' and self.total_amount < 0.0:
                return self.party.supplier_payment_type
            else:
                return self.payment_type


class Opportunity:
    __metaclass__ = PoolMeta
    __name__ = 'sale.opportunity'

    def _get_sale_opportunity(self):
        sale = super(Opportunity, self)._get_sale_opportunity()
        if sale.party and sale.party.customer_payment_type:
            sale.payment_type = self.party.customer_payment_type
        return sale
