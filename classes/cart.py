#!/usr/bin/env python3
import threading
import requests
from xmltodict import parse
import json
import re
import webbrowser
from classes.logger import Logger
from classes.tools import Tools

log = Logger().log
tools = Tools()
config = tools.load('config/config.json')

cart_dict = []

class Cart:

    def __init__(self, session, lock):
        self.session = session
        self.lock = lock

    def add_to_cart(self,keywords,size):
        #print(self.session)
        session = self.session
        lock = self.lock

        response = session.get('https://shop-usa.palaceskateboards.com/sitemap_products_1.xml')

        data = parse(response.content)
        data = json.loads(json.dumps(data))
        data = data['urlset']['url']
        item_url = ''
        item_id = ''
        item_name = ''

        # Find item
        for item in data[1:]:
            if all(i in item['image:image']['image:title'].lower() for i in keywords):
                log('Item found: ' + str(item['image:image']['image:title']),'yellow')
                item_url = item['loc']
                item_name = item['image:image']['image:title']

        if item_url=='':
            log('Item not found, retrying...','error')
        else:
            page = session.get(item_url+'.json')
            #page_data = parse(page.content)
            page_data = json.loads(page.text)

            for item in page_data['product']['variants']:
                if(size.lower() == item['title'].lower()):
                    log('Variant found for size ' + item['title'] + ': ' + str(item['id']),'yellow')
                    item_id = item['id']
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
                log('Successfully added ' + item_name + ' to cart','success')
            lock.release()
            #webbrowser.open_new_tab(item_url)


        #for items in data['products']:
        #    print(items['title'])


    def check_cart(self):
        session = self.session
        response = session.get('https://shop-usa.palaceskateboards.com/cart.js')
        data = response.json()
        data = json.loads(json.dumps(data))
        log('---------- Cart ----------', 'lightpurple')
        log('Item Count: ' + str(data['item_count']),'yellow')
        global cart_dict
        for item in data['items']:
            log(' - ' + item['title'] + ' - ' + str(item['quantity']), 'yellow')
            item = {'updates[' + str(item['id']) + ']': str(item['quantity'])}
            cart_dict.append(item)

    def checkout(self):
        session = self.session
        log('Starting Checkout Process..','info')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
        }

        # Grab the payload information
        resp = session.get('https://shop-usa.palaceskateboards.com/cart/')

        note = re.findall('(input type=\"hidden\" name=\"note\" id=\"note\" value=\")([\w|\d]+)',resp.text)[0][1]
        updates = re.findall('(updates[)([\d]+])',resp.text)

        log('Payload Note: ' + note,'yellow')

        # Sanity Check
        if len(cart_dict) == len(updates):
            log('Payload QTY Matches - ' + str(len(updates)) + ' items in cart ✓' ,'success')
        else:
            log('Payload QTY not matching','error')

        # Make payload
        payload = {
            'note': note,
            'checkout': 'Checkout',
        }
        # Update / concat payloads
        for d in cart_dict:
            payload.update(d)

        header_checkout = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '70',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'shop-usa.palaceskateboards.com',
            'Origin': 'https://shop-usa.palaceskateboards.com',
            'Referer': 'https://shop-usa.palaceskateboards.com/cart',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # Send checkout
        checkout0 = session.post('https://shop-usa.palaceskateboards.com/cart', headers=header_checkout, data=payload, allow_redirects=True)
        log('At Checkout - URL: ' + checkout0.url,'pink')
        
