from collections import namedtuple
from itertools import groupby

Line = namedtuple('Line', 'url keys impressions'.split())


data = []
with open('result-tiu.csv') as f:
    next(f)

    for line in f:
        line = line.strip()
        if not line:
            continue
        words = line.split('|')
        if len(words) != 6:
            print('FUCKKKK!')
            continue
        url, keys, clicks, impressions, ctr, position = words
        impressions = int(impressions)

        data.append(Line(
            url=url,
            keys=keys,
            impressions=impressions,
        ))

data = sorted(data, key=lambda i: (i.url, i.impressions), reverse=True)

for key, group in groupby(data, key=lambda i: i.url):

    count = 0
    for item in group:
        print(f'{item.url}|{item.keys}|{item.impressions}')

        count += 1
        if count == 2:
            break




