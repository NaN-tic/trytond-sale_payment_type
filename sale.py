#This file is part of sale_payment_type module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['PaymentType', 'Sale']

_STATES = {
    'readonly': Eval('state') != 'draft',
}
_DEPENDS = ['state']
ZERO = Decimal('0.0')


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

    def _get_grouped_invoice_domain(self, invoice):
        invoice_domain = super(Sale, self)._get_grouped_invoice_domain(invoice)

        # know about the invoice is payable or receivable payment type (untaxed amount)
        # _get_grouped_invoice_domain not return an invoice with lines and untaxed
        # amount; we need to recompute those values
        if not hasattr(invoice, 'untaxed_amount'):
            has_lines = hasattr(invoice, 'lines')
            if not has_lines:
                invoice_lines = []
                for line in self.lines:
                    if line.type == 'line':
                        iline, = line.get_invoice_line()
                        setattr(iline, 'amount', iline.on_change_with_amount())
                        invoice_lines.append(iline)
                invoice.lines = invoice_lines
            invoice.on_change_lines()
            # reset lines
            if not has_lines:
                invoice.lines = []

        invoice_domain.append(
            ('payment_type', '=', self._get_invoice_payment_type(invoice)))
        return invoice_domain

    def _get_invoice_sale(self):
        invoice = super(Sale, self)._get_invoice_sale()
        if self.payment_type:
            # set None payment type to control payable/receivable kind
            # depend untaxed amount
            invoice.payment_type = None
        return invoice

    def create_invoice(self):
        invoice = super(Sale, self).create_invoice()

        if invoice:
            payment_type = self._get_invoice_payment_type(invoice)
            if payment_type:
                invoice.payment_type = payment_type
                invoice.save()
        return invoice

    def _get_invoice_payment_type(self, invoice):
        if not self.payment_type:
            return None

        if invoice.untaxed_amount >= ZERO:
            kind = 'receivable'
            name = 'customer_payment_type'
        else:
            kind = 'payable'
            name = 'supplier_payment_type'

        if self.payment_type.kind == kind:
            return self.payment_type
        else:
            payment_type = getattr(self.party, name)
            if payment_type:
                return payment_type
        return None
