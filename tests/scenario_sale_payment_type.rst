==========================
Sale Payment Type Scenario
==========================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Install account_payment_type Module::

    >>> config = activate_modules('sale_payment_type')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

Create tax::

    >>> tax = set_tax_code(create_tax(Decimal('.10')))
    >>> tax.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('50')
    >>> template.cost_price = Decimal('25')
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.customer_taxes.append(tax)
    >>> template.salable = True
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create payment type::

    >>> PaymentType = Model.get('account.payment.type')
    >>> receivable = PaymentType(name='Receivable', kind='receivable')
    >>> receivable.save()
    >>> payable = PaymentType(name='Payable', kind='payable')
    >>> payable.save()
    >>> both = PaymentType(name='Both', kind='both')
    >>> both.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.customer_payment_type = receivable
    >>> party.supplier_payment_type = payable
    >>> party.save()

Check invoice payment type is correctly assigned::

    >>> Sale = Model.get('sale.sale')
    >>> sale = Sale()
    >>> sale.party = party
    >>> sale.payment_term = payment_term
    >>> sale.payment_type == receivable
    True
    >>> line = sale.lines.new()
    >>> line.product = product
    >>> line.quantity = 1
    >>> line.unit_price = Decimal('50.0')
    >>> sale.untaxed_amount
    Decimal('50.00')
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> invoice, = sale.invoices
    >>> invoice.payment_type == receivable
    True

The supplier payment term is used for return sales::

    >>> sale = Sale()
    >>> sale.party = party
    >>> sale.payment_term = payment_term
    >>> sale.payment_type == receivable
    True
    >>> line = sale.lines.new()
    >>> line.product = product
    >>> line.quantity = -1
    >>> line.unit_price = Decimal('50.0')
    >>> sale.untaxed_amount
    Decimal('-50.00')
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> invoice, = sale.invoices
    >>> invoice.payment_type == payable
    True

When using a both payment the payment_type of the sale is used::

    >>> sale = Sale()
    >>> sale.party = party
    >>> sale.payment_term = payment_term
    >>> sale.payment_type = both
    >>> line = sale.lines.new()
    >>> line.product = product
    >>> line.quantity = -1
    >>> line.unit_price = Decimal('50.0')
    >>> sale.untaxed_amount
    Decimal('-50.00')
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> invoice, = sale.invoices
    >>> invoice.payment_type == both
    True
