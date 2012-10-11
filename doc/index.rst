Sale Payment Type Module
########################

The sale_payment_type tryton module adds payment type to sale process.
The sale order inherits payment type from party as default. Then, the invoice
based on this sale order inherits the payment information from it.
Also computes payment type of invoices created from picking lists (extracted
from party info).
