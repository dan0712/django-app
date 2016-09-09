from common.structures import ChoiceEnum


class OrderStatus(ChoiceEnum):
    New = 1,
    Submitted = 2,
    PartiallyFilled = 3,
    Filled = 4,
    Cancelled = 5,
    Unknown = 6


class Order(object):
    def __init__(self, order, contract, ib_id, symbol, remaining):
        self.order = order
        self.contract = contract
        self.ib_id = ib_id

        self.symbol = symbol
        self.status = OrderStatus.New
        self.remaining = remaining
        self.fill_price = None
        self.filled = 0

