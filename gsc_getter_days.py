'''
by Геннадий Сивашов

Файл для ежедневной выгрузки. Сохраняет результат в папку GSC
Именно этот файл стоит добавлять в шедулер

Как запускать: в терминале пишем:
1. Для Ubuntu и MAC: source .venv/bin/activate
1. Для Windows: source .venv/Scripts/activate

Если .venv уже активировано то:
2. python gsc_getter_days.py https://site.com/`

ВАЖНО: если вы меняете поля в этом файле, то также необходимо поменять поля в ga_bigquery/gsc_transfer_to_bigquery.py
sc-domain:sitename.com
Либо удалить либо добавить поля schema
'''


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
# это заголовок. Если в будущем Вы хотите что-то менять, то надо будет от сюда либо удалить либо изменить/добавить поле



def main(argv):
    for days_back in range(3, 490):
        service, flags = sample_tools.init(
            argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
            scope='https://www.googleapis.com/auth/webmasters.readonly')

        start_date = (date.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        end_date = start_date
        file_name = f'GSC_{start_date.replace("-", "")}.csv'
        with open(Path().cwd() / 'GSC' / file_name, 'w', encoding='utf-8') as csv_file:
            csv_file.write(f'{"|".join(FIELDS)}\n')

            row_limit = 25000
            processed_rows = None

            while True:
                start_row = (processed_rows or 0)

                request = {
                    'startDate': start_date,
                    'endDate': end_date,
                    'dimensions': ['date', 'page', 'query', 'device'], # при необходимости можно менять но читайте шапку файла
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
                        calenar_date, page, query, device = row['keys']
                        # query = ''.join(query.strip().split('|')).replace('  ', ' ')
                        query = query.replace('|', '').replace('  ', ' ')
                        key_fields = calenar_date, page, query, device
                        keys = u'|'.join(key_fields)
                        keys = _escape(keys)
                        csv_file.write('{keys}|{clicks}|{impressions}|{ctr}|{position}\n'.format(keys=keys,clicks=row['clicks'],impressions=row['impressions'],ctr=row['ctr'],position=row['position']))

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
