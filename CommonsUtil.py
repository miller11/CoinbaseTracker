from boto3.dynamodb.conditions import Key
from datetime import datetime
import os
from coinbase.wallet.client import Client
import boto3
import pytz
import json

LONDON_TMZ = pytz.timezone('Europe/London')


class CommonsUtil:
    HEADERS = {
        "Access-Control-Allow-Origin": "*",  # Required for CORS support to work
        "Access-Control-Allow-Headers": "Content-Type, Authorization, Origin, X-Auth-Token",
        "Access-Control-Allow-Methods": "GET, POST, PATCH, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Credentials": True  # Required for cookies, authorization headers with HTTPS
    }

    NO_ACCOUNT_RESPONSE = {
        "statusCode": 404,
        "body": json.dumps({
            "message": "No account_id query string param was passed"
        }),
    }

    @staticmethod
    def get_cb_client():
        return Client(os.getenv('API_KEY'), os.getenv('API_SECRET'))

    @staticmethod
    def get_dynamo_table(table_name):
        if 'AWS_KEY_ID' in os.environ:
            session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_KEY_SECRET'))
        else:
            session = boto3.Session()

        dynamodb = session.resource('dynamodb', region_name='us-east-1')

        return dynamodb.Table(table_name)

    @staticmethod
    def _normalize_timestamp(epoch_time):
        return LONDON_TMZ.localize(datetime.fromtimestamp(epoch_time)).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_transactions(account_id):
        table = CommonsUtil.get_dynamo_table('cb-bot-transaction')

        response = table.query(
            KeyConditionExpression=Key('account_id').eq(account_id)
        )

        transaction_list = response['Items']

        for transaction in transaction_list:
            transaction['timestamp'] = CommonsUtil._normalize_timestamp(transaction['timestamp'])

        return transaction_list
