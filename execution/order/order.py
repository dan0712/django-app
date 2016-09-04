import uuid


class Order(object):
    def __init__(self, order, contract, ib_id):
        self.order = order
        self.contract = contract
        self.ib_id = ib_id
        self.new = True
