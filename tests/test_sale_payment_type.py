#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This file is part of sale_payment_type module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class SalePaymentTypeTestCase(unittest.TestCase):
    'Test SalePaymentType module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('sale_payment_type')

    def test0005views(self):
        'Test views'
        test_view('sale_payment_type')

    def test0006depends(self):
        'Test depends'
        test_depends()

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        SalePaymentTypeTestCase))
    return suite
