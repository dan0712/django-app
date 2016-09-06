#http://interactivebrokers.github.io/tws-api/financial_advisor_methods_and_orders.html#financial_advisor_orders&gsc.tab=0


class Profiles(object):
    start_faProfile = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + \
                      "<ListOfAllocationProfiles>"

    start_account_faProfile = "<AllocationProfile>" + \
                              "<name>%s</name>" + \
                              "<type>3</type>" + \
                              "<ListOfAllocations varName=\"listOfAllocations\">"

    share_allocation = "<Allocation>" + \
                       "<acct>%s</acct>" + \
                       "<amount>%.1f</amount>" + \
                       "</Allocation>"

    end_account_faProfile = "</ListOfAllocations>" + \
                            "</AllocationProfile>"

    end_faProfile = "</ListOfAllocationProfiles>"


class FAAccountProfile(object):
    def __init__(self):
        self.profile = Profiles.start_faProfile

    def append_share_allocation(self, ticker, account_dict):
        self.profile += Profiles.start_account_faProfile % ticker
        for account, alloc in account_dict.items():
            self.profile += Profiles.share_allocation % (account, alloc)
        self.profile += Profiles.end_account_faProfile

    def get_profile(self):
        return self.profile + Profiles.end_faProfile


if __name__ == '__main__':
    daco = FAAccountProfile()

    account_dict = dict()
    account_dict['DU493341'] = 30
    account_dict['DU493342'] = 40

    daco.append_share_allocation('MSFT', account_dict)
    daco.append_share_allocation('AAPL', account_dict)
    profile = daco.get_profile()
    print('a')
