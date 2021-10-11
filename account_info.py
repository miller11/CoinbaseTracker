import os
from accounts.AccountSummaryUtil import AccountSummaryUtil

if __name__ == '__main__':
    summary_util = AccountSummaryUtil()

    for account in summary_util.get_raw_accounts():
        print(account)
