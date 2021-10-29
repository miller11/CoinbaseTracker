import os
from datetime import datetime

from botocore.config import Config
from accounts.AccountUtil import AccountSummaryUtil
import boto3
import time

TABLE_NAME = 'ross-gains'
DATABASE_NAME = 'realized-gains'
CLOUDWATCH_NAMESPACE = 'coinbase-tracking'
CURRENT_MILLI_TIME = round(time.time() * 1000)


def build_record(r_dimensions, r_name, r_value):
    return {
        'Dimensions': r_dimensions,
        'MeasureName': r_name,
        'MeasureValue': str(r_value),
        'MeasureValueType': 'DOUBLE',
        'Time': str(CURRENT_MILLI_TIME)
    }


def build_metric(m_dimensions, m_name, m_value):
    return {
            'MetricName': m_name,
            'Dimensions': m_dimensions,
            'Value': float(m_value),
            'Unit': 'None',
            'Timestamp': datetime.fromtimestamp(CURRENT_MILLI_TIME/1000.0)
        }


def write_timestream(t_session, t_records):
    client = t_session.client('timestream-write', config=Config(read_timeout=20, max_pool_connections=5000,
                                                              retries={'max_attempts': 10}))

    try:
        result = client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME, Records=t_records, CommonAttributes={})
        print("TimeStream WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
    except client.exceptions.RejectedRecordsException as err:
        print("ERROR RejectedRecords: ", err)
        for rr in err.response["RejectedRecords"]:
            print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        print("Other records were written successfully. ")
        raise Exception(err)
    except Exception as err:
        print("ERROR:", err)
        raise Exception(err)


def write_metrics(m_session, m_records):
    client = m_session.client('cloudwatch')
    try:
        result = client.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=m_records)
        print("CloudWatch WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
    except Exception as err:
        print("ERROR:", err)
        raise Exception(err)


if __name__ == '__main__':
    # pull ssm param for jira account
    ssm = boto3.client('ssm', region_name='us-east-1')
    api_key = ssm.get_parameter(Name='/ic-miller/realized-coinbase/coinbase/api-key', WithDecryption=True)['Parameter']['Value']
    api_secret = ssm.get_parameter(Name='/ic-miller/realized-coinbase/coinbase/api-secret', WithDecryption=True)['Parameter']['Value']

    summary_util = AccountSummaryUtil(api_key, api_secret)

    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_KEY_SECRET'),
    )

    records = []
    metrics = []
    account_dimensions = [
        {'Name': 'wallet', 'Value': 'ross'},
        {'Name': 'type', 'Value': 'account'}
    ]

    # gain
    records.append(build_record(account_dimensions, 'gain', summary_util.get_total_gains().amount))
    metrics.append(build_metric(account_dimensions, 'gain', summary_util.get_total_gains().amount))

    # balance
    records.append(build_record(account_dimensions, 'balance', summary_util.get_current_balance().amount))
    metrics.append(build_metric(account_dimensions, 'balance', summary_util.get_current_balance().amount))

    # investment
    records.append(build_record(account_dimensions, 'investment', summary_util.get_current_investment().amount))
    metrics.append(build_metric(account_dimensions, 'investment', summary_util.get_current_investment().amount))

    for account_summary in summary_util.get_acct_summaries():
        dimensions = [
            {'Name': 'wallet', 'Value': 'ross'},
            {'Name': 'type', 'Value': account_summary['name']}
        ]

        # gain
        records.append(build_record(dimensions, 'gain', account_summary['realized_gains'].amount))
        metrics.append(build_metric(dimensions, 'gain', account_summary['realized_gains'].amount))

        # balance
        records.append(build_record(dimensions, 'balance', account_summary['balance'].amount))
        metrics.append(build_metric(dimensions, 'balance', account_summary['balance'].amount))

        # investment
        records.append(build_record(dimensions, 'investment', account_summary['investment'].amount))
        metrics.append(build_metric(dimensions, 'investment', account_summary['investment'].amount))

        # write data to timestream
        write_timestream(session, records)

        # write metrics to CloudWatch
        write_metrics(session, metrics)

