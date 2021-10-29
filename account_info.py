import os
from accounts.AccountUtil import AccountSummaryUtil, AccountUtil, MockAccountUtil
from accounts.UserAccountUtil import check_user_account

if __name__ == '__main__':
    # summary_util = AccountSummaryUtil()
    #
    # for account in summary_util.get_raw_accounts():
    #     print(account)
    #
    #

    user_id = '70f772da-6555-41c9-818f-8d5b7b21b5eb'
    # account_id = 'f476634d-d6eb-52aa-a338-70d1d4de65e0'
    fake_account_id = 'obviouslyNotAnAccountId'

    print(check_user_account(user_id, fake_account_id))
