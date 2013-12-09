# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Not

__all__ = ['Template']
__metaclass__ = PoolMeta


class Template:
    __name__ = 'product.template'

    check_purchase_expiry_margin = fields.Boolean('Check Expiry margin on '
        'Purchases', help='If checked the sistem won\'t allow to post stock '
        ' moves related to purchases if the expriy dates doesn\'t exceed the '
        'margin set.')
    purchase_expiry_margin = fields.Integer('Expiry margin on Purchases',
        help='Minimum days to consider a purchased expiry lot valid on '
        'purchases', states={
            'invisible': Not(Eval('purchase_expiry_dates_margin', False)),
            'required': Eval('purchase_expiry_dates_margin', False),
            }, depends=['purchase_expiry_dates_margin'])

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        cls._sql_constraints += [
            ('purchase_expiry_margin',
                'CHECK(COALESCE(purchase_expiry_margin,0) >= 0)',
                'Expiry margin must be greater than 0'),
            ]
