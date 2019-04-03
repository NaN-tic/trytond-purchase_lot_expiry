# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import date, timedelta
from trytond.pool import Pool, PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Move']


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

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
                not self.lot.expiration_date or
                not self.product.template.check_purchase_expiry_margin):
            return

        delta = timedelta(days=self.product.template.purchase_expiry_margin)
        max_use_date = date.today() + delta
        if self.lot.expiration_date > max_use_date:
            return

        raise UserError(gettext('purchase_lot_expiry.msg_expired_lot_margin',
            lot=self.lot.rec_name,
            move=self.rec_name,
            purchase=self.origin.purchase.rec_name,
            ))
