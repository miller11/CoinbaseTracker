import os
from coinbase.wallet.client import Client
from money import Money


class AccountSummaryUtil:
    def __init__(self):
        self.accounts = []
        self.account_summaries = []
        self.init_summaries()

    def get_acct_summaries(self):
        return self.account_summaries

    def get_raw_accounts(self):
        return self.accounts

    def get_total_gains(self):
        return sum([i['realized_gains'] for i in self.account_summaries])

    def get_current_investment(self):
        return sum([i['investment'] for i in self.account_summaries])

    def get_current_balance(self):
        return sum([i['balance'] for i in self.account_summaries])

    def init_summaries(self):
        client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'))
        self.accounts = client.get_accounts(limit=50).data

        for account in self.accounts:
            all_transactions = []

            if account.created_at is not None:
                transactions = account.get_transactions()
                all_transactions.extend(transactions.data)

                while transactions.pagination is not None and transactions.pagination.next_starting_after is not None:
                    transactions = client.get_transactions(account_id=account.id,
                                                           starting_after=transactions.pagination.next_starting_after)
                    all_transactions.extend(transactions.data)

                total_investment = 0.0

                for transaction in all_transactions:
                    total_investment += float(transaction.native_amount.amount)

                account_summary = {
                    'name': account.currency_pair,
                    'balance': Money(account.native_balance.amount, 'USD'),
                    'investment': Money(total_investment, 'USD'),
                    'realized_gains': Money(account.native_balance.amount, 'USD') - Money(total_investment, 'USD')
                }

                self.account_summaries.append(account_summary)
