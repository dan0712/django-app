import numpy as np

class SingleLevelMarketDepth(object):
    def __init__(self, bid=float('nan'), ask=float('nan'), bid_volume=float('nan'), ask_volume=float('nan')):
        self.bid = bid
        self.ask = ask
        self.bid_volume = bid_volume
        self.ask_volume = ask_volume

    def __str__(self):
        return "bidVolume: %s, bid: %s, ask: %s, askVolume: %s" % (self.bid_volume,
                                                                   self.bid,
                                                                   self.ask,
                                                                   self.ask_volume)

    @property
    def is_complete(self):
        if not np.isnan(self.bid) and not np.isnan(self.ask) and not np.isnan(self.bid_volume) and not np.isnan(self.ask_volume):
            return True
        else:
            return False

    def get_mid(self):
        if self.is_complete:
            return (self.bid + self.ask)/2.0

    __repr__ = __str__


class MarketDepth(object):
    def __init__(self, max_level=10):
        self.levels = [SingleLevelMarketDepth() for i in range(0, max_level)]

    @property
    def depth(self):
        return len(self.levels)

    def get_level(self, level=0):
        if len(self.levels) > level:
            return self.levels[level]
        else:
            return SingleLevelMarketDepth()

    def add_level(self, level, single_level_depth):
        self.levels[level] = single_level_depth

    def __repr__(self):
        output = ""
        for i in range(0, len(self.levels)):
            output += "\nlevel %s: %s" % (i, self.levels[i])
        return output
