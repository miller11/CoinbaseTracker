import os
from datetime import datetime

import yfinance as yf
import pytz

import boto3
from boto3.dynamodb.conditions import Key

from GraphUtil import GraphUtil

LONDON_TMZ = pytz.timezone('Europe/London')
TIME_PERIOD = '14d'
TIME_INTERVAL = '30m'


def get_dynamo_table(table_name):
    if 'AWS_KEY_ID' in os.environ:
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_KEY_SECRET'))
    else:
        session = boto3.Session()

    dynamodb = session.resource('dynamodb', region_name='us-east-1')

    return dynamodb.Table(table_name)


def _normalize_timestamp(epoch_time):
    return LONDON_TMZ.localize(datetime.fromtimestamp(epoch_time)).strftime('%Y-%m-%d %H:%M:%S')


def get_transactions(account_id):
    table = get_dynamo_table('cb-bot-transaction')

    response = table.query(
        KeyConditionExpression=Key('account_id').eq(account_id)
    )

    transaction_list = response['Items']

    for transaction in transaction_list:
        transaction['timestamp'] = _normalize_timestamp(transaction['timestamp'])

    return transaction_list


def get_account(account_id):
    table = get_dynamo_table('cb-mock-account')

    response = table.query(
        KeyConditionExpression=Key('account_id').eq(account_id),
    )

    return response['Items'][0]

def get_buys():
    return [d for d in transactions if d['operation'] == 'BUY']


def get_sells():
    return [d for d in transactions if d['operation'] == 'SELL']


if __name__ == '__main__':
    account_identifier = 'bec75c28-d95a-52a9-8edf-d0947a133eda'

    # Get the account
    account = get_account(account_identifier)

    # Get the transactions
    transactions = get_transactions(account_id=account_identifier)

    # Importing market data
    data = yf.download(tickers=account['currency'] + '-USD', period=TIME_PERIOD, interval=TIME_INTERVAL)

    # Define Graph Util
    figure = GraphUtil(data)

    # Add plot lines for the buys
    for buy in get_buys():
        figure.add_account_buy(str(buy['timestamp']))

    # Add plot lines for the sells
    for sell in get_sells():
        figure.add_account_sell(str(sell['timestamp']))

    # Show the graph figure
    figure.show_figure()
    # figure.write_html()

