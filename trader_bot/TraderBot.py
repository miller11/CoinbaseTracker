import os
import time
import json
import boto3
from boto3.dynamodb.conditions import Key
from coinbase.wallet.client import Client
from InvestmentUtil import InvestmentUtil, calculate_coinbase_fee
from dataclasses import dataclass


@dataclass
class TraderBotConfig:
    def __init__(self, json_string):
        self.__dict__ = json.loads(json_string)

    account_id: str
    default_buy: float = 100
    interval: str = '30m'
    short_term_periods: int = 5
    long_term_periods: int = 20


def get_aws_session():
    if 'AWS_KEY_ID' in os.environ:
        return boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_KEY_SECRET'))
    else:
        return boto3.Session()


def get_dynamo_table(table_name):
    dynamodb = get_aws_session().resource('dynamodb', region_name='us-east-1')

    return dynamodb.Table(table_name)


class TraderBot:
    def __init__(self, config: TraderBotConfig):
        self.config = config
        self.account = None
        self.currency_pair = None
        self.last_transaction = None
        # self.account = self.__get_account()  # Fetch the account from CB
        # self.currency_pair = self.account['currency'] + '-USD'
        # self.last_transaction = self.__get_last_transaction()  # Get last transaction

    def setup(self):
        self.account = self._get_account()
        self.currency_pair = self.account['currency'] + '-USD'
        self.last_transaction = self._get_last_transaction()  # Get last transaction

        return self

    def execute_actions(self):
        investment_util = InvestmentUtil(currency_pair=self.currency_pair, interval=self.config.interval,
                                         short_term_periods=self.config.short_term_periods,
                                         long_term_periods=self.config.long_term_periods)

        # If transaction exists
        if self.last_transaction is not None:
            if self.last_transaction['operation'] == 'BUY':
                # Currently invested check sell
                if investment_util.should_sell(buy_amount=float(self.last_transaction['amount']),
                                               sell_amount=float(self.account['native_balance']['amount'])):
                    self._record_decision(investment_util.get_decision(), investment_util.get_reason(),
                                           investment_util.get_margin())
                    self._put_transaction(investment_util.get_decision(), self.account['native_balance']['amount'])
                    print('Account is currently invested and bot has determined a SELL')
                else:
                    self._record_decision(investment_util.get_decision(), investment_util.get_reason())
                    print('Account is currently invested and bot has determined a HOLD')
            else:
                # Currently not invested check buy
                if investment_util.should_buy():
                    self._record_decision(investment_util.get_decision(), investment_util.get_reason())
                    self._put_transaction(investment_util.get_decision(),
                                           self.last_transaction['amount'] - calculate_coinbase_fee(
                                               self.last_transaction['amount']))

                    print('Account is not currently invested and bot has determined a BUY')
                else:
                    self._record_decision(investment_util.get_decision(), investment_util.get_reason())
                    print('Account is not currently invested and bot has determined a HOLD')
        else:
            # If no transaction and SMA is below LMA buy - margin
            long_term_average = investment_util.long_term_average()
            short_term_average = investment_util.short_term_average()
            if short_term_average < (long_term_average - (long_term_average * .015)):
                self._record_decision('BUY',
                                       f'Short term average is below the long term average + 1.5%. '
                                       f'SMA: {short_term_average}. LMA: {long_term_average}. ')
                self._put_transaction('BUY', self.config.default_buy - calculate_coinbase_fee(self.config.default_buy))
                print('Account has no previous transactions. Bot has determined a BUY')
            else:
                # Else hold until better market conditions
                self._record_decision('HOLD',
                                       f'Short term average is NOT below the long term average + 1.5%. '
                                       f'SMA: {short_term_average}. LMA: {long_term_average}. ')
                print('HOLD')

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

    def _put_transaction(self, operation, amount):
        table = get_dynamo_table('cb-bot-transaction')
        transaction = {
            'account_id': self.config.account_id,
            'timestamp': int(time.time()),
            'operation': operation,
            'amount': str(amount),
            'currency_pair': self.currency_pair
        }

        if operation == 'SELL':
            transaction['currency_value'] = self._get_sell_price()
        else:
            transaction['currency_value'] = self._get_buy_price()

        response = table.put_item(
            Item=transaction
        )

        return response

    @staticmethod
    def _get_cb_client():
        ssm = get_aws_session().client('ssm', region_name='us-east-1')
        api_key = ssm.get_parameter(
            Name='/ic-miller/realized-coinbase/coinbase/api-key',
            WithDecryption=True)['Parameter']['Value']
        api_secret = ssm.get_parameter(
            Name='/ic-miller/realized-coinbase/coinbase/api-secret',
            WithDecryption=True)['Parameter']['Value']

        return Client(api_key, api_secret)

    def _get_account(self):
        client = self._get_cb_client()

        return client.get_account(account_id=self.config.account_id)

    def _get_buy_price(self):
        client = self._get_cb_client()

        currency_pair = self.currency_pair

        # todo handle smarter for sol
        if str(currency_pair).startswith("SOL"):
            currency_pair = "SOL-USD"

        return client.get_buy_price(currency_pair=currency_pair).amount

    def _get_sell_price(self):
        client = self._get_cb_client()

        return client.get_sell_price(currency_pair=self.currency_pair).amount

    def _record_decision(self, decision, reason, margin=None):
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
