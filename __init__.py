#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from .product import *
from .stock import *


def register():
    Pool.register(
        Template,
        Move,
        module='purchase_lot_expiry', type_='model')
