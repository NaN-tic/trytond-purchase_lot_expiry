# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import date, timedelta
from trytond.pool import Pool, PoolMeta

__all__ = ['Move']
__metaclass__ = PoolMeta


class Move:
    __name__ = 'stock.move'

    @classmethod
    def __setup__(cls):
        super(Move, cls).__setup__()
        cls._error_messages.update({
            'expired_lot_margin': 'The lot "%(lot)s" of Stock Move "%(move)s"'
                ' related to purchase "%(purchase)s" doesn\'t exceed'
                ' the safety margin configured in the product.',
            })

    @classmethod
    def do(cls, moves):
        for move in moves:
            move.check_lot_purchase_margin()
        super(Move, cls).do(moves)

    def check_lot_purchase_margin(self):
        pool = Pool()
        PurchaseLine = pool.get('purchase.line')
        if (self.from_location.type != 'supplier' or not self.lot or
                not self.origin or not isinstance(self.origin, PurchaseLine) or
                not self.lot.expiry_date or
                not self.product.template.check_purchase_expiry_margin or
                self.to_location.allow_expired):
            return

        delta = timedelta(days=self.product.template.purchase_expiry_margin)
        max_use_date = date.today() + delta
        if self.lot.expiry_date > max_use_date:
            return

        self.raise_user_error('expired_lot_margin', {
                'lot': self.lot.rec_name,
                'move': self.rec_name,
                'purchase': self.origin.purchase.rec_name,
                })
