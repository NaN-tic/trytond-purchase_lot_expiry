# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from sql.conditionals import Coalesce
from trytond.model import fields, Check
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Not

__all__ = ['Template']
__metaclass__ = PoolMeta


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'

    check_purchase_expiry_margin = fields.Boolean('Check Expiry margin on '
        'Purchases', help='If checked the sistem won\'t allow to post stock '
        'moves related to purchases if its lot\'s expriy date doesn\'t exceed '
        'the margin set.')
    purchase_expiry_margin = fields.Integer('Expiry margin on Purchases',
        help='Minimum days to consider a purchased expiry lot valid on '
        'purchases', states={
            'invisible': Not(Eval('check_purchase_expiry_margin', False)),
            'required': Eval('check_purchase_expiry_margin', False),
            }, depends=['check_purchase_expiry_margin'])

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('purchase_expiry_margin',
                Check(t, Coalesce(t.purchase_expiry_margin, 0) >= 0),
                'Expiry margin must be greater than 0'),
            ]
