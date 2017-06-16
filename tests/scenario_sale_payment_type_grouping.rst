==========================
Sale Payment Type Scenario
==========================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard, Report
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install sale_payment_type::

    >>> Module = Model.get('ir.module')
    >>> module1, module2 = Module.find([('name', 'in', [
    ...    'sale_payment_type', 'sale_invoice_grouping'])])
    >>> module1.click('install')
    >>> module2.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

    >>> Journal = Model.get('account.journal')
    >>> cash_journal, = Journal.find([('type', '=', 'cash')])
    >>> cash_journal.credit_account = cash
    >>> cash_journal.debit_account = cash
    >>> cash_journal.save()

Create tax::

    >>> tax = create_tax(Decimal('.10'))
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
    >>> template.type = 'goods'
    >>> template.salable = True
    >>> template.list_price = Decimal('10')
    >>> template.cost_price = Decimal('5')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.supplier_taxes.append(tax)
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

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.sale_invoice_grouping_method = 'standard'
    >>> party.customer_payment_type = receivable
    >>> party.supplier_payment_type = payable
    >>> party.save()

Sale with payment type payable::

    >>> Sale = Model.get('sale.sale')
    >>> SaleLine = Model.get('sale.line')
    >>> sale = Sale()
    >>> sale.party = party
    >>> sale.payment_term = payment_term
    >>> sale.payment_type = receivable
    >>> sale.invoice_method = 'order'
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = 2.0
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = 3.0
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> sale.state
    u'processing'
    >>> invoice, = sale.invoices
    >>> invoice.payment_type == receivable
    True

Sale with payment type payable and negative untaxed amount::

    >>> sale = Sale()
    >>> sale.party = party
    >>> sale.payment_term = payment_term
    >>> sale.payment_type = receivable
    >>> sale.invoice_method = 'order'
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = -2.0
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = -3.0
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> sale.state
    u'processing'
    >>> invoice, = sale.invoices
    >>> invoice.payment_type == payable
    True

Group other sale with payment type payable and negative untaxed amount::

    >>> sale = Sale()
    >>> sale.party = party
    >>> sale.payment_term = payment_term
    >>> sale.payment_type = receivable
    >>> sale.invoice_method = 'order'
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = -2.0
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = -3.0
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> sale.state
    u'processing'
    >>> invoice, = sale.invoices
    >>> invoice.payment_type == payable
    True
    >>> len(invoice.lines)
    4
    >>> line1, line2, line3, line4 = invoice.lines
    >>> line1.origin.sale.number
    u'2'
    >>> line3.origin.sale.number
    u'3'
