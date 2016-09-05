import uuid
from enum import Enum, unique
from common.structures import ChoiceEnum


class OrderStatus(ChoiceEnum):
    New = 1,
    Submitted = 2,
    PartiallyFilled = 3,
    Filled = 4,
    Expired = 5


class Order(object):
    def __init__(self, order, contract, ib_id):
        self.order = order
        self.contract = contract
        self.ib_id = ib_id

        self.status = OrderStatus.New
        self.remaining = self.order.m_totalQuantity
        self.fill_price = None
        self.filled = 0
