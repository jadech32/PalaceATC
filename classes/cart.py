#!/usr/bin/env python3
import threading
import requests
from xmltodict import parse
import json
import webbrowser
from classes.logger import logger

class cart:

    def __init__(self, session, lock):
        self.session = session
        self.lock = lock

    def add_to_cart(self,keywords,size):
        #print(self.session)
        session = self.session
        lock = self.lock

        response = session.get('https://shop-usa.palaceskateboards.com/sitemap_products_1.xml')
        log = logger().log
        data = parse(response.content)
        data = json.loads(json.dumps(data))
        data = data['urlset']['url']
        item_url = ''
        item_id = ''
        item_name = ''

        # Find item
        for item in data[1:]:
            if all(i in item['image:image']['image:title'].lower() for i in keywords):
                print(log('Item found: ' + str(item['image:image']['image:title']),'yellow'))
                item_url = item['loc']
                item_name = item['image:image']['image:title']

        if item_url=='':
            log('Item not found, retrying...','error')
        else:
            page = session.get(item_url+'.xml')
            page_data = parse(page.content)
            page_data = json.loads(json.dumps(page_data))

            for item in page_data['hash']['variants']['variant']:
                if(size.lower() == item['title'].lower()):
                    log('Variant found for size ' + item['title'] + ': ' + item['id']['#text'],'yellow')
                    item_id = item['id']['#text']

                    break;

            # add to session cart
            payload = {
                'id': item_id,
                'quantity': '1'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
            }
            lock.acquire()
            add = session.post('https://shop-usa.palaceskateboards.com/cart/add.js', data=payload, headers=headers)
            if '200' in str(add.status_code):
                log('Successfully added ' + item_name + ' to cart','yellow')
            lock.release()
            #webbrowser.open_new_tab(item_url)


        #for items in data['products']:
        #    print(items['title'])

    def check_cart(self):
        log = logger().log
        session = self.session
        response = session.get('https://shop-usa.palaceskateboards.com/cart.js')
        data = response.json()
        data = json.loads(json.dumps(data))
        log('---------- Cart ----------', 'lightpurple')
        log('Item Count: ' + str(data['item_count']),'yellow')
        for item in data['items']:
            log('    ' + item['title'] + ' - ' + str(item['quantity']), 'yellow')
