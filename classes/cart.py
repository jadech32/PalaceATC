#!/usr/bin/env python3

import requests
from xmltodict import parse
import json
from classes.logger import logger

class cart:

    def __init__(self, session):
        self.session = session

    def add_to_cart(self,keywords):
        print(self.session)
        session = self.session

        response = session.get('https://shop-usa.palaceskateboards.com/sitemap_products_1.xml')
        log = logger().log
        data = parse(response.content)
        data = json.loads(json.dumps(data))
        data = data['urlset']['url']
        item_url = ''

        # Find item
        for item in data[1:]:
            if all(i in item['image:image']['image:title'].lower() for i in keywords):
                print(log('Item found: ' + str(item['image:image']['image:title']),'yellow'))
                item_url = item['loc']
'''
        if item_url=='':
            log('Item not found, retrying...','error')
'''



        #for items in data['products']:
        #    print(items['title'])
