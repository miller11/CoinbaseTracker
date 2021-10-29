import boto3
import os
from datetime import datetime

ONE_GB_IN_BYTES = 1073741824


class TimeseriesUtil:
    def __init__(self):
        if 'AWS_KEY_ID' in os.environ:
            session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_KEY_SECRET'))
        else:
            session = boto3.Session()

        query_client = session.client('timestream-query')

        self.paginator = query_client.get_paginator('query')

    def run_query(self, query_string):
        try:
            page_iterator = self.paginator.paginate(QueryString=query_string)

            all_data = []

            for page in page_iterator:
                all_data.extend(self._parse_query_result(page))

            return all_data
        except Exception as err:
            print("Exception while running query:", err)

    def get_bytes_scanned(self):
        return self.bytes_scanned_gb

    def get_bytes_metered(self):
        return self.bytes_metered_gb

    def _parse_query_result(self, query_result):
        query_status = query_result["QueryStatus"]

        self.bytes_scanned_gb = float(query_status["CumulativeBytesScanned"]) / ONE_GB_IN_BYTES
        print(f"Data scanned so far: {self.bytes_scanned_gb} GB")

        self.bytes_metered_gb = float(query_status["CumulativeBytesMetered"]) / ONE_GB_IN_BYTES
        print(f"Data metered so far: {self.bytes_metered_gb} GB")

        column_info = query_result['ColumnInfo']

        row_data = []

        for row in query_result['Rows']:
            row_data.append(self._parse_row(column_info, row))

        return row_data

    def _parse_row(self, column_info, row):
        data = row['Data']
        row_output = {}
        for j in range(len(data)):
            info = column_info[j]
            datum = data[j]

            if 'ScalarType' in info['Type']:
                if info['Type']['ScalarType'] == 'TIMESTAMP':
                    row_output.update({info['Name']: str(datetime.fromisoformat(datum['ScalarValue'].split('.')[0]))})
                else:
                    row_output.update({info['Name']: datum['ScalarValue']})
            else:
                row_output.update({info['Name']: self._parse_datum(info, datum)})

        return row_output

    def _parse_datum(self, info, datum):
        if datum.get('NullValue', False):
            return "%s=NULL" % info['Name'],

        column_type = info['Type']

        # If the column is of TimeSeries Type
        if 'TimeSeriesMeasureValueColumnInfo' in column_type:
            return self._parse_time_series(info, datum)

        # If the column is of Array Type
        elif 'ArrayColumnInfo' in column_type:
            array_values = datum['ArrayValue']
            return "%s=%s" % (info['Name'], self._parse_array(info['Type']['ArrayColumnInfo'], array_values))

        # If the column is of Row Type
        elif 'RowColumnInfo' in column_type:
            row_column_info = info['Type']['RowColumnInfo']
            row_values = datum['RowValue']
            return self._parse_row(row_column_info, row_values)

        # If the column is of Scalar Type
        else:
            return self._parse_column_name(info) + datum['ScalarValue']

    def _parse_time_series(self, info, datum):
        time_series_output = []
        for data_point in datum['TimeSeriesValue']:
            time_series_output.append("{time=%s, value=%s}"
                                      % (data_point['Time'],
                                         self._parse_datum(info['Type']['TimeSeriesMeasureValueColumnInfo'],
                                                           data_point['Value'])))
        return "[%s]" % str(time_series_output)

    def _parse_array(self, array_column_info, array_values):
        array_output = []
        for datum in array_values:
            array_output.append(self._parse_datum(array_column_info, datum))

        return "[%s]" % str(array_output)

    @staticmethod
    def _parse_column_name(info):
        if 'Name' in info:
            return info['Name'] + "="
        else:
            return ""
