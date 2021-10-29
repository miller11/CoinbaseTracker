import os
from coinbase.wallet.client import Client
import boto3
from money import Money


def get_cb_client():
    return Client(os.getenv('API_KEY'), os.getenv('API_SECRET'))


def get_dynamo_table(table_name):
    if 'AWS_KEY_ID' in os.environ:
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_KEY_SECRET'))
    else:
        session = boto3.Session()

    dynamodb = session.resource('dynamodb', region_name='us-east-1')

    return dynamodb.Table(table_name)



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
        client = get_cb_client()
        self.accounts = AccountUtil.get_accounts()

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
                    'name': account.currency,
                    'balance': Money(account.native_balance.amount, 'USD'),
                    'investment': Money(total_investment, 'USD'),
                    'realized_gains': Money(account.native_balance.amount, 'USD') - Money(total_investment, 'USD')
                }

                self.account_summaries.append(account_summary)


class AccountUtil:
    @staticmethod
    def get_accounts():
        return get_cb_client().get_accounts(limit=50).data


class MockAccountUtil:
    @staticmethod
    def get_accounts():
        table = get_dynamo_table('cb-mock-account')
        response = table.scan()

        return response['Items']

