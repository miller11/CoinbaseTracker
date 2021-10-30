import os

from boto3.dynamodb.conditions import Key

from accounts.AccountUtil import AccountSummaryUtil, AccountUtil, MockAccountUtil, get_dynamo_table
from accounts.UserAccountUtil import check_user_account
from datetime import datetime, timedelta
import time


def get_bot_decisions(account_identifier):
    table = get_dynamo_table('cb-bot-decision')

    query_time = datetime.today() - timedelta(days=14)

    response = table.query(
        KeyConditionExpression=Key('account_id').eq(account_identifier) & Key('timestamp').gt(int(query_time.timestamp()))
    )

    for item in response['Items']:
        item['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['timestamp']))

    return response['Items']


if __name__ == '__main__':
    # summary_util = AccountSummaryUtil()
    #
    # for account in summary_util.get_raw_accounts():
    #     print(account)
    #
    #

    user_id = '70f772da-6555-41c9-818f-8d5b7b21b5eb'
    account_id = 'f476634d-d6eb-52aa-a338-70d1d4de65e0'
    fake_account_id = 'obviouslyNotAnAccountId'

    # print(check_user_account(user_id, fake_account_id))

    print(get_bot_decisions(account_id))

