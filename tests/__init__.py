# This file is part of sale_payment_type module for Tryton.  The COPYRIGHT file
# at the top level of this repository contains the full copyright notices and
# license terms.
try:
    from trytond.modules.sale_payment_type.tests.test_sale_payment_type import suite
except ImportError:
    from .test_sale_payment_type import suite

__all__ = ['suite']
