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
    while True:
        start_row = (processed_rows or 0)
        request = {
            'startDate': flags.start_date,
            'endDate': flags.end_date,
            'dimensions': ['page'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'device',
                    'expression': 'desktop'  # change to 'mobile' if needed
                }]
            }],
            'rowLimit': row_limit,
            'startRow': start_row
        }

        response = execute_request(service, flags.property_uri, request)

        # # TODO: only for debug {
        # print('request', request)
        # print('response len', len(response['rows']))
        # # }
        for row in response['rows']:
            get_url_queries(row['keys'][0], service, flags)

        len_rows = len(response['rows'])
        processed_rows = start_row + len_rows
        if len_rows != row_limit:
            break


# new request for list of urls from first step
def get_url_queries(url, service, flags):

    row_limit = 25000
    processed_rows = None

    print('Url|Keys|Clicks|Impressions|CTR|Position')

    while True:
        start_row = (processed_rows or 0)
        # print(url)
        request = {
            'startDate': flags.start_date,
            'endDate': flags.end_date,
            'dimensions': ['query'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'expression': url
                }]
            }],
            'rowLimit': row_limit,
            'startRow': start_row + 1
        }

        response = execute_request(service, flags.property_uri, request)
        if 'rows' not in response:
            break
        # print(response)
        print_table(response, 'Top Queries for %s' % url, url)

        len_rows = len(response['rows'])
        processed_rows = start_row + len_rows
        if len_rows != row_limit:
            break


def execute_request(service, property_uri, request):
    return service.searchanalytics().query(
        siteUrl=property_uri, body=request).execute()


def print_table(response, title, url):
    if 'rows' not in response:
        print('No rows in response')
        print('Responce is:', response)
        return

    rows = response['rows']

    for row in rows:
        keys = ''
        if 'keys' in row:
            keys = u'|'.join(row['keys'])
        print('{url}|{keys}|{clicks}|{impressions}|{ctr}|{position}'.format(
            url=url,
            keys=keys,
            clicks=row['clicks'],
            impressions=row['impressions'],
            ctr=row['ctr'],
            position=row['position']
        ))


if __name__ == '__main__':
    main(sys.argv)
