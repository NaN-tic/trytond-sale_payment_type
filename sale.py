# This file is part of sale_payment_type module for Tryton.  The COPYRIGHT file
# at the top level of this repository contains the full copyright notices and
# license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['PaymentType', 'Sale', 'Opportunity']

_STATES = {
    'readonly': Eval('state') != 'draft',
}
_DEPENDS = ['state']
ZERO = Decimal('0.0')


class PaymentType(metaclass=PoolMeta):
    __name__ = 'account.payment.type'

    @classmethod
    def __setup__(cls):
        super(PaymentType, cls).__setup__()
        cls._check_modify_related_models.add(('sale.sale', 'payment_type'))


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'
    payment_type = fields.Many2One('account.payment.type', 'Payment Type',
        domain=[
            ('kind', 'in', ['both', 'receivable']),
            ],
        states=_STATES, depends=_DEPENDS)


    @classmethod
    def default_payment_type(cls):
        PaymentType = Pool().get('account.payment.type')
        payment_types = PaymentType.search(cls.payment_type.domain)
        if len(payment_types) == 1:
            return payment_types[0].id

    def on_change_party(self):
        self.payment_type = None
        super(Sale, self).on_change_party()
        if self.party and self.party.customer_payment_type:
            self.payment_type = self.party.customer_payment_type

    def _get_grouped_invoice_domain(self, invoice):
        invoice_domain = super(Sale, self)._get_grouped_invoice_domain(invoice)

        # know about the invoice is payable or receivable payment type (untaxed
        # amount) _get_grouped_invoice_domain not return an invoice with lines
        # and untaxed amount; we need to recompute those values
        if not hasattr(invoice, 'untaxed_amount'):
            invoice.untaxed_amount = self.untaxed_amount

        invoice_domain.append(
            ('payment_type', '=', self._get_invoice_payment_type(invoice)))
        return invoice_domain

    def _get_invoice_sale(self):
        invoice = super(Sale, self)._get_invoice_sale()
        if self.payment_type:
            # set None payment type to control payable/receivable kind
            # depend untaxed amount
            invoice.payment_type = None
            if hasattr(self.payment_type, 'bank_account'):
                invoice.bank_account = None
        return invoice

    def create_invoice(self):
        invoice = super(Sale, self).create_invoice()

        if invoice:
            payment_type = self._get_invoice_payment_type(invoice)
            if payment_type:
                invoice.payment_type = payment_type
                if hasattr(invoice, 'bank_account'):
                    invoice._get_bank_account()
                invoice.save()
        return invoice

    def _get_invoice_payment_type(self, invoice):
        if self.payment_type and self.payment_type.kind == 'both':
            return self.payment_type

        if invoice.untaxed_amount >= ZERO:
            kind = 'receivable'
            name = 'customer_payment_type'
        else:
            kind = 'payable'
            name = 'supplier_payment_type'

        if self.payment_type and self.payment_type.kind == kind:
            return self.payment_type
        else:
            payment_type = getattr(self.party, name)
            return payment_type if payment_type else None


class Opportunity(metaclass=PoolMeta):
    __name__ = 'sale.opportunity'

    def _get_sale_opportunity(self):
        sale = super(Opportunity, self)._get_sale_opportunity()
        if sale.party and sale.party.customer_payment_type:
            sale.payment_type = self.party.customer_payment_type
        return sale
