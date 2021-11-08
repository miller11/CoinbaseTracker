import time

from boto3.dynamodb.conditions import Key

from CommonsUtil import CommonsUtil
from accounts.AccountUtil import AccountUtil


def check_user_account(user_id, account_id):
    table = CommonsUtil.get_dynamo_table('cb_user_accounts')

    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )

    cached_accounts = response['Items']

    if any(cached_account['account_id'] == account_id for cached_account in cached_accounts):
        return True

    accounts = AccountUtil.get_accounts()

    has_match = False

    for account in accounts:
        if account.created_at is not None:
            if account['id'] == account_id:
                has_match = True

            if not any(cached_account['account_id'] == account_id for cached_account in cached_accounts):
                cached_account = {
                    'user_id': user_id,
                    'account_id': account['id'],
                    'timestamp': int(time.time()),
                }

                table.put_item(
                    Item=cached_account
                )

    return has_match
