import os
import json
import time
import boto3
from coinbase.wallet.client import Client
from dataclasses import dataclass
from boto3.dynamodb.conditions import Key

from .InvestmentUtil import InvestmentUtil, calculate_coinbase_fee


def get_cb_client():
    ssm = get_aws_session().client('ssm', region_name='us-east-1')
    api_key = ssm.get_parameter(
        Name='/ic-miller/realized-coinbase/coinbase/api-key',
        WithDecryption=True)['Parameter']['Value']
    api_secret = ssm.get_parameter(
        Name='/ic-miller/realized-coinbase/coinbase/api-secret',
        WithDecryption=True)['Parameter']['Value']

    return Client(api_key, api_secret)


def get_aws_session():
    if 'AWS_KEY_ID' in os.environ:
        return boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_KEY_SECRET'))
    else:
        return boto3.Session()


@dataclass
class TraderBotConfig:
    def __init__(self, json_string):
        self.__dict__ = json.loads(json_string)

    account_id: str
    currency: str
    default_buy: float = 100
    interval: str = '30m'
    short_term_periods: int = 5
    long_term_periods: int = 20

    def get_currency_pair(self):
        return self.currency + '-USD'


class TraderBot:
    def __init__(self, config: TraderBotConfig, investment_util: InvestmentUtil):
        self.config = config
        self.investment_util = investment_util
        self.account = None
        self.currency_pair = None
        self.last_transaction = None
        self.decision = None

    def setup(self):
        self.account = self._get_account()
        self.currency_pair = self.account['currency'] + '-USD'
        self.last_transaction = self._get_last_transaction()  # Get last transaction

        return self

    def execute_actions(self):
        # If transaction exists
        if self.last_transaction is not None:
            if self.last_transaction['operation'] == 'BUY':
                # Currently invested check sell
                if self.investment_util.should_sell(buy_amount=float(self.last_transaction['amount']),
                                                    sell_amount=float(self.account['native_balance']['amount'])):
                    self._record_decision(self.investment_util.get_decision(), self.investment_util.get_reason(),
                                          self.investment_util.get_margin())
                    self._execute_transaction(self.investment_util.get_decision(),
                                              self.account['native_balance']['amount'])
                    print('Account is currently invested and bot has determined a SELL')
                else:
                    self._record_decision(self.investment_util.get_decision(), self.investment_util.get_reason())
                    print('Account is currently invested and bot has determined a HOLD')
            else:
                # Currently not invested check buy
                if self.investment_util.should_buy():
                    self._record_decision(self.investment_util.get_decision(), self.investment_util.get_reason())
                    self._execute_transaction(self.investment_util.get_decision(),
                                              float(self.last_transaction['amount']) - calculate_coinbase_fee(
                                                  self.last_transaction['amount']))

                    print('Account is not currently invested and bot has determined a BUY')
                else:
                    self._record_decision(self.investment_util.get_decision(), self.investment_util.get_reason())
                    print('Account is not currently invested and bot has determined a HOLD')
        else:
            # If no transaction and SMA is below LMA buy - margin
            long_term_average = self.investment_util.long_term_average()
            short_term_average = self.investment_util.short_term_average()
            if short_term_average < (long_term_average - (long_term_average * .015)):
                self._record_decision('BUY',
                                      f'Short term average is below the long term average + 1.5%. '
                                      f'SMA: {short_term_average}. LMA: {long_term_average}. ')
                self._execute_transaction('BUY',
                                          self.config.default_buy - calculate_coinbase_fee(self.config.default_buy))
                print('Account has no previous transactions. Bot has determined a BUY')
            else:
                # Else hold until better market conditions
                self._record_decision('HOLD',
                                      f'Short term average is NOT below the long term average + 1.5%. '
                                      f'SMA: {short_term_average}. LMA: {long_term_average}. ')
                print('HOLD')

    def _get_account(self):
        client = get_cb_client()

        return client.get_account(account_id=self.config.account_id)

    def _get_last_transaction(self):
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

    def get_decision(self):
        return self.decision

    def get_buy_price(self):
        client = get_cb_client()

        currency_pair = self.currency_pair

        # todo handle smarter for sol
        if str(currency_pair).startswith("SOL"):
            currency_pair = "SOL-USD"

        return client.get_buy_price(currency_pair=currency_pair).amount

    def get_sell_price(self):
        client = get_cb_client()

        currency_pair = self.currency_pair

        # todo handle smarter for sol
        if str(currency_pair).startswith("SOL"):
            currency_pair = "SOL-USD"

        return client.get_sell_price(currency_pair=currency_pair).amount

    def _execute_transaction(self, operation, amount):
        table = get_dynamo_table('cb-bot-transaction')
        transaction = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'amount': str(amount),
            'currency_pair': self.currency_pair
        }

        if operation == 'SELL':
            transaction['currency_value'] = self.get_sell_price()
        else:
            transaction['currency_value'] = self.get_buy_price()

        response = table.put_item(
            Item=transaction
        )

        return response

    def _record_decision(self, decision, reason, margin=None):
        table = get_dynamo_table('cb-bot-decision')
        self.decision = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'decision': decision,
            'reason': reason
        }

        if margin is not None:
            self.decision['margin'] = str(margin)

        response = table.put_item(
            Item=self.decision
        )

        return response


def get_dynamo_table(table_name):
    dynamodb = get_aws_session().resource('dynamodb', region_name='us-east-1')

    return dynamodb.Table(table_name)