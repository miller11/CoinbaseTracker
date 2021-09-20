import os
from coinbase.wallet.client import Client


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'))

    account_summaries = []
    accounts = client.get_accounts(limit=50)

    for account in accounts.data:
        all_transactions = []

        if account.created_at is not None:
            transactions = account.get_transactions()
            all_transactions.extend(transactions.data)

            while transactions.pagination is not None and transactions.pagination.next_starting_after is not None:
                transactions = client.get_transactions(account_id=account.id, starting_after=transactions.pagination.next_starting_after)
                all_transactions.extend(transactions.data)

            total_investment = 0.0

            for transaction in all_transactions:
                total_investment += float(transaction.native_amount.amount)

            account_summary = {
                'name': account.currency,
                'balance': float(account.native_balance.amount),
                'investment': total_investment,
                'realized gains': float(account.native_balance.amount) - total_investment
            }

            account_summaries.append(account_summary)
            print(account_summary)

    total_gains = sum([i['realized gains'] for i in account_summaries])
    print(total_gains)


