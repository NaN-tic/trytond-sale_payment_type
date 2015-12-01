# This file is part of the sale_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class SalePaymentTypeTestCase(ModuleTestCase):
    'Test Sale Payment Type module'
    module = 'sale_payment_type'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        SalePaymentTypeTestCase))
    return suite