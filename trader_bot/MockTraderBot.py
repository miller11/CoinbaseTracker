from boto3.dynamodb.conditions import Key
from TraderBot import TraderBotConfig, TraderBot, get_dynamo_table


class MockTraderBot(TraderBot):
    def __get_account(self):
        # Get the account from the mock-account table
        table = get_dynamo_table('cb-mock-account')
        response = table.query(
            KeyConditionExpression=Key('account_id').eq(self.config.account_id),
            Limit=1
        )

        account = response['Items'][0]

        # if sell set balance to zero
        if self.last_transaction['operation'] == 'SELL':
            account['native_balance']['amount'] = 0
        else:
            # if buy look at buy price, and look up current price
            buy_price = self.last_transaction['currency_value']
            cur_price = self.__get_buy_price()

            # determine multiplier (cur_price - buy_price) / buy_price) * 100
            multiplier = ((cur_price - buy_price) / buy_price)

            # determine balance buy taking buy amount * multiplier
            buy_amount = self.last_transaction['amount']
            account['native_balance']['amount'] = buy_amount * multiplier

        return account
