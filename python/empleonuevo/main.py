#!/usr/bin/env python
import requests
from lxml import html
import re

url = 'https://www.empleonuevo.com/empleo-en/comercial-de-aceros-y-perfiles-frontera'
xpath = '/html/body/div[1]/div/div/main/div/div[1]/section[2]/div/div/div[2]/div[2]/div/div[2]/div/div[2]'
pattern_venta = '^venta|^Venta'

response = requests.get(url=url)
#print(response.content)
html_source = response.content


tree = html.fromstring(html_source)
text = tree.xpath(xpath)
for element in text:
    for div in element:
        try:
            if re.search(pattern=pattern_venta, string=div.text_content()):
                print(div.text_content())
                print(f"https://www.empleonuevo.com{div.getchildren()[0].values()[0]}")
        except Exception:
            pass
