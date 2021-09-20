from util.AccountSummaryUtil import AccountSummaryUtil

if __name__ == '__main__':
    summaryUtil = AccountSummaryUtil()

    print(summaryUtil.get_acct_summaries())

    print(summaryUtil.get_total_gains())
