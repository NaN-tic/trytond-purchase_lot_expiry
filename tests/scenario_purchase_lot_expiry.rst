=================
Purchase Scenario
=================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> from trytond.exceptions import UserError
    >>> today = datetime.date.today()

Install stock Module::

    >>> config = activate_modules('purchase_lot_expiry')

Create company::

    >>> _ = create_company()
    >>> company = get_company()
    >>> party = company.party

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> payable = accounts['payable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']
    >>> account_cash = accounts['cash']

Create parties::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Create account categories::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.save()

    >>> account_category_tax, = account_category.duplicate()
    >>> account_category_tax.supplier_taxes.append(tax)
    >>> account_category_tax.save()

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
    >>> template.purchasable = True
    >>> template.list_price = Decimal('10')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_category = account_category_tax
    >>> template.check_purchase_expiry_margin = True
    >>> template.purchase_expiry_margin = 5
    >>> template.expiration_time = 10
    >>> template.save()
    >>> product.template = template
    >>> product.cost_price = Decimal('5')
    >>> product.save()

Create lots::

    >>> Lot = Model.get('stock.lot')
    >>> invalid_lot = Lot()
    >>> invalid_lot.number = '001'
    >>> invalid_lot.product = product
    >>> invalid_lot.expiration_date = today + relativedelta(days=4)
    >>> invalid_lot.save()
    >>> valid_lot = Lot()
    >>> valid_lot.number = '002'
    >>> valid_lot.product = product
    >>> valid_lot.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Purchase a product::

    >>> Purchase = Model.get('purchase.purchase')
    >>> PurchaseLine = Model.get('purchase.line')
    >>> purchase = Purchase()
    >>> purchase.party = supplier
    >>> purchase.payment_term = payment_term
    >>> purchase.invoice_method = 'order'
    >>> purchase_line = PurchaseLine()
    >>> purchase.lines.append(purchase_line)
    >>> purchase_line.product = product
    >>> purchase_line.quantity = 2.0
    >>> purchase.save()
    >>> purchase.click('quote')
    >>> purchase.click('confirm')
    >>> purchase.click('process')
    >>> purchase.state
    'processing'
    >>> purchase.reload()
    >>> len(purchase.moves), len(purchase.shipment_returns), len(purchase.invoices)
    (1, 0, 1)
    >>> invoice, = purchase.invoices
    >>> invoice.origins == purchase.rec_name
    True

Validate Shipments::

    >>> Move = Model.get('stock.move')
    >>> ShipmentIn = Model.get('stock.shipment.in')
    >>> shipment = ShipmentIn()
    >>> shipment.supplier = supplier
    >>> for move in purchase.moves:
    ...     incoming_move = Move(id=move.id)
    ...     incoming_move.lot= invalid_lot
    ...     shipment.incoming_moves.append(incoming_move)
    >>> shipment.save()
    >>> shipment.origins == purchase.rec_name
    True
    >>> try:
    ...     ShipmentIn.receive([shipment.id], config.context)
    ... except UserError as e:
    ...     e.message
    'The lot "001" of Stock Move "2u product" related to purchase "1" doesn\'t exceed the safety margin configured in the product.'
    >>> for move in shipment.moves:
    ...     move.lot= valid_lot
    ...     move.save()
    >>> ShipmentIn.receive([shipment.id], config.context)
    >>> ShipmentIn.done([shipment.id], config.context)
    >>> purchase.reload()
    >>> len(purchase.shipments), len(purchase.shipment_returns)
    (1, 0)
