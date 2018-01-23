# This file is part of sale_payment_type module for Tryton.  The COPYRIGHT file
# at the top level of this repository contains the full copyright notices and
# license terms.

from trytond.pool import Pool
from . import sale


def register():
    Pool.register(
        sale.PaymentType,
        sale.Sale,
        sale.Opportunity,
        module='sale_payment_type', type_='model')
