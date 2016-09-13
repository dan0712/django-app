#http://interactivebrokers.github.io/tws-api/financial_advisor_methods_and_orders.html#financial_advisor_orders&gsc.tab=0


class Profiles(object):
    START_FA_PROFILE = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + \
                      "<ListOfAllocationProfiles>"

    START_ACCOUNT_FA_PROFILE = "<AllocationProfile>" + \
                              "<name>%s</name>" + \
                              "<type>3</type>" + \
                              "<ListOfAllocations varName=\"listOfAllocations\">"

    SHARE_ALLOCATION = "<Allocation>" + \
                       "<acct>%s</acct>" + \
                       "<amount>%.1f</amount>" + \
                       "</Allocation>"

    END_ACCOUNT_FA_PROFILE = "</ListOfAllocations>" + \
                            "</AllocationProfile>"

    END_FA_PROFILE = "</ListOfAllocationProfiles>"


class FAAccountProfile(object):
    '''
    Create allocation scheme for specific share.
    E.g. wa want to buy 100 shares of MSFT, but want to allocate 50 to 1 IB account and 1 to another.
    Thus, we send such allocation scheme to IB, before submitting order.
    '''
    def __init__(self):
        self.profile = Profiles.START_FA_PROFILE

    def append_share_allocation(self, ticker, account_dict):
        self.profile += Profiles.START_ACCOUNT_FA_PROFILE % ticker
        for account, alloc in account_dict.items():
            self.profile += Profiles.SHARE_ALLOCATION % (account, alloc)
        self.profile += Profiles.END_ACCOUNT_FA_PROFILE

    def get_profile(self):
        return self.profile + Profiles.END_FA_PROFILE


if __name__ == '__main__':
    daco = FAAccountProfile()

    account_dict = dict()
    account_dict['DU493341'] = 30
    account_dict['DU493342'] = 40

    daco.append_share_allocation('MSFT', account_dict)
    daco.append_share_allocation('AAPL', account_dict)
    profile = daco.get_profile()
    print('a')
