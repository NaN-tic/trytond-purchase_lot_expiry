#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from . import product
from . import stock


def register():
    Pool.register(
        product.Template,
        product.Product,
        stock.Move,
        module='purchase_lot_expiry', type_='model')
