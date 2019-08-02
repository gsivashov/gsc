import argparse
import sys
from pathlib import Path
from googleapiclient import sample_tools
from datetime import date, timedelta

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('property_uri', type=str,
                       help=('Site or app URI to query data for (including '
                             'trailing slash).'))

FIELDS = ['Date', 'Page', 'Query', 'Device', 'Clicks', 'Impressions', 'CTR', 'Position']

start_date = (date.today() - timedelta(days=3)).strftime('%Y-%m-%d')
end_date = start_date


def main(argv):
    service, flags = sample_tools.init(
        argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
        scope='https://www.googleapis.com/auth/webmasters.readonly')

    file_name = f'GSC_{start_date.replace("-", "")}.csv'
    with open(Path().cwd() / 'GSC' / file_name, 'w') as csv_file:
        csv_file.write(f'{"|".join(FIELDS)}\n')

        row_limit = 25000
        processed_rows = None

        while True:
            start_row = (processed_rows or 0)

            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['date', 'page', 'query', 'device'],
                # 'dimensionFilterGroups': [{
                #     'filters': [{
                #         'dimension': 'device',
                #         'expression': 'mobile'
                #     }]
                # }],
                'rowLimit': row_limit,
                'startRow': start_row
            }

            response = execute_request(service, flags.property_uri, request)

            if 'rows' not in response:
                print('No rows in response')
                print('Responce is:', response)
                return

            rows = response['rows']

            for row in rows:
                keys = ''
                if 'keys' in row:
                    keys = u'|'.join(row['keys'])
                    keys = _escape(keys)
                csv_file.write('{keys}|{clicks}|{impressions}|{ctr}|{position}\n'.format(
                    keys=keys,
                    clicks=row['clicks'],
                    impressions=row['impressions'],
                    ctr=row['ctr'],
                    position=row['position']
                ))

            len_rows = len(response['rows'])
            processed_rows = start_row + len_rows
            if len_rows != row_limit:
                break


def _escape(source):
    _source = source.replace('"', '')
    return f'{_source}'


def execute_request(service, property_uri, request):
    return service.searchanalytics().query(
        siteUrl=property_uri, body=request).execute()


if __name__ == '__main__':
    main(sys.argv)
