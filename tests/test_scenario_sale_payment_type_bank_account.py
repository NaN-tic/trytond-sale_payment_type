import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear, create_tax,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    create_payment_term, set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install sale_payment_type and account_bank
        activate_modules(['sale_payment_type', 'account_bank'])

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create tax
        tax = create_tax(Decimal('.10'))
        tax.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        product = Product()
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.cost_price_method = 'fixed'
        template.account_category = account_category
        product, = template.products
        product.cost_price = Decimal('5')
        template.save()
        product, = template.products

        # Create payment term
        payment_term = create_payment_term()
        payment_term.save()

        # Create payment type
        PaymentType = Model.get('account.payment.type')
        receivable = PaymentType(name='Receivable', kind='receivable')
        receivable.account_bank = 'party'
        receivable.save()
        payable = PaymentType(name='Payable', kind='payable')
        payable.save()
        both = PaymentType(name='Both', kind='both')
        both.save()

        # Create bank account
        Party = Model.get('party.party')
        Bank = Model.get('bank')
        BankAccount = Model.get('bank.account')
        bparty = Party()
        bparty.name = 'Bank'
        bparty.save()
        bank = Bank(party=bparty)
        bank.save()
        bank_account = BankAccount()
        bank_account.bank = bank
        bank_number = bank_account.numbers.new()
        bank_number.type = 'iban'
        bank_number.number = 'BE82068896274468'
        bank_number = bank_account.numbers.new()
        bank_number.type = 'other'
        bank_number.number = 'not IBAN'
        bank_account.save()

        # Create party
        party = Party(name='Party')
        party.customer_payment_type = receivable
        party.supplier_payment_type = payable
        party.bank_accounts.append(bank_account)
        party.receivable_bank_account = bank_account
        party.save()

        # Sale with payment type payable
        Sale = Model.get('sale.sale')
        SaleLine = Model.get('sale.line')
        sale = Sale()
        sale.party = party
        sale.payment_term = payment_term
        sale.payment_type = receivable
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product
        sale_line.quantity = 2.0
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product
        sale_line.quantity = 3.0
        sale.click('quote')
        sale.click('confirm')
        sale.click('process')
        self.assertEqual(sale.state, 'processing')

        invoice, = sale.invoices
        self.assertEqual(invoice.payment_type, receivable)
        self.assertEqual(invoice.bank_account, bank_account)
