import re

with open('sitemap_products-5.xml') as sitemap:
    sitemap = sitemap.read()
    line = re.findall('<loc>(.*?)</loc>', sitemap)

with open('sitemap_product_urls.txt', 'w') as new_file:
    for url in line:
        new_file.write(url + '\n')
