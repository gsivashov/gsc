"""
Sample usage:

  $ PYTHONIOENCODING=utf-8 py search_analytics_api_sample.py 'https://www.example.com/' '2018-08-01' '2018-08-01'

"""

import argparse
import sys
from googleapiclient import sample_tools

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('property_uri', type=str,
                       help=('Site or app URI to query data for (including '
                             'trailing slash).'))
argparser.add_argument('start_date', type=str,
                       help=('Start date of the requested date range in '
                             'YYYY-MM-DD format.'))
argparser.add_argument('end_date', type=str,
                       help=('End date of the requested date range in '
                             'YYYY-MM-DD format.'))


def main(argv):
    service, flags = sample_tools.init(
        argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
        scope='https://www.googleapis.com/auth/webmasters.readonly')

    row_limit = 25000
    processed_rows = None

    print('Keys|Country|Device|Clicks|Impressions|CTR|Position')

    while True:
        start_row = (processed_rows or 0)

        request = {
            'startDate': flags.start_date,
            'endDate': flags.end_date,
            'dimensions': ['query', 'country', 'device'],
            'searchType': 'web',
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'country',
                    'expression': 'can'
                }]
            }],
            'rowLimit': row_limit,
            'startRow': start_row
        }

        response = execute_request(service, flags.property_uri, request)
        print_table(response, 'Top Queries')

        len_rows = len(response['rows'])
        processed_rows = start_row + len_rows
        if len_rows != row_limit:
            break


def execute_request(service, property_uri, request):
    return service.searchanalytics().query(
        siteUrl=property_uri, body=request).execute()


def print_table(response, title):
    if 'rows' not in response:
        print('No rows in response')
        print('Responce is:', response)
        return

    rows = response['rows']

    for row in rows:
        keys = ''
        if 'keys' in row:
            keys = u'|'.join(row['keys'])
        print('{keys}|{clicks}|{impressions}|{ctr}|{position}'.format(
            keys=keys,
            clicks=row['clicks'],
            impressions=row['impressions'],
            ctr=row['ctr'],
            position=row['position']
        ))


if __name__ == '__main__':
    main(sys.argv)
