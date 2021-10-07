import os
import time
import boto3
from boto3.dynamodb.conditions import Key
from coinbase.wallet.client import Client
from util.InvestmentUtil import InvestmentUtil
from dataclasses import dataclass


@dataclass
class TraderBotConfig:
    account_id: str
    default_buy: float = 100
    interval: str = '30m'
    short_term_periods: int = 5
    long_term_periods: int = 20


def get_dynamo_table(table_name):
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_KEY_SECRET'),
    )

    dynamodb = session.resource('dynamodb', region_name='us-east-1')

    return dynamodb.Table(table_name)


def get_currency_usd(account):
    return account.currency + '-USD'


class TraderBot:
    def __init__(self, config: TraderBotConfig):
        self.config = config

    def execute_actions(self):
        # Fetch the account from CB
        account = self.get_account()

        # Get last transaction
        last_transaction = self.get_last_transaction()
        investment_util = InvestmentUtil(currency_type=get_currency_usd(account), interval=self.config.interval,
                                         short_term_periods=self.config.short_term_periods,
                                         long_term_periods=self.config.long_term_periods)

        # If transaction exists
        if last_transaction is not None:
            if last_transaction['operation'] == 'BUY':
                # Currently invested check sell
                if investment_util.should_sell(buy_amount=float(last_transaction['amount']),
                                               sell_amount=float(account.native_balance.amount)):
                    self.record_decision(investment_util.get_decision(), investment_util.get_reason(),
                                         investment_util.get_margin())
                    self.put_transaction(investment_util.get_decision(), account.native_balance.amount)
                    print('Account is currently invested and bot has determined a SELL')
                else:
                    self.record_decision(investment_util.get_decision(), investment_util.get_reason())
                    print('Account is currently invested and bot has determined a HOLD')
            else:
                # Currently not invested check buy
                if investment_util.should_buy():
                    self.record_decision(investment_util.get_decision(), investment_util.get_reason())
                    self.put_transaction(investment_util.get_decision(), last_transaction['amount'])
                    print('Account is not currently invested and bot has determined a BUY')
                else:
                    self.record_decision(investment_util.get_decision(), investment_util.get_reason())
                    print('Account is not currently invested and bot has determined a HOLD')
        else:
            # If no transaction and SMA is below LMA buy - margin
            long_term_average = investment_util.long_term_average()
            short_term_average = investment_util.short_term_average()
            if short_term_average < (long_term_average - (long_term_average * .015)):
                self.record_decision('BUY',
                                     f'Short term average is below the long term average + 1.5%. '
                                     f'SMA: {short_term_average}. LMA: {long_term_average}. ')
                self.put_transaction('BUY', self.config.default_buy)
                print('Account has no previous transactions. Bot has determined a BUY')
            else:
                # Else hold until better market conditions
                self.record_decision('HOLD',
                                     f'Short term average is NOT below the long term average + 1.5%. '
                                     f'SMA: {short_term_average}. LMA: {long_term_average}. ')
                print('HOLD')

    def get_last_transaction(self):
        table = get_dynamo_table('cb-bot-transaction')

        # Expression attribute names can only reference items in the projection expression.
        response = table.query(
            KeyConditionExpression=Key('account_id').eq(self.config.account_id),
            ScanIndexForward=False,
            Limit=1
        )

        if len(response['Items']) == 0:
            return None

        return response['Items'][0]

    def put_transaction(self, operation, amount):
        table = get_dynamo_table('cb-bot-transaction')
        transaction = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'operation': operation,
            'amount': str(amount)
        }

        response = table.put_item(
            Item=transaction
        )

        return response

    def get_account(self):
        client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'))

        return client.get_account(account_id=self.config.account_id)

    def record_decision(self, decision, reason, margin=None):
        table = get_dynamo_table('cb-bot-decision')
        bot_decision = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'decision': decision,
            'reason': reason
        }

        if margin is not None:
            bot_decision['margin'] = str(margin)

        response = table.put_item(
            Item=bot_decision
        )

        return response
