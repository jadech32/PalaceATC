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
        log('--------------------------', 'lightpurple')
    def checkout(self, queue):
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

        # Queue Handling
        printed = 0
        while 'throttle' in checkout0.url:
            if printed == 0:
                log('In Queue..','info')
                printed = 1

        if printed == 1:
            log('Exited Queue..','success')
        log('At Shipping Info - URL: ' + checkout0.url,'pink')
        if 'stock_problem' in checkout0.url:
            log('Stock Problem, exiting program..','error')
            exit()

        # Authenticity Token
        auth_token = re.findall('(name=\"authenticity_token\" value=\")([^\"]*)',checkout0.text)[0][1]
        url_ship = str(checkout0.url) + '?step=contact_information'

        headers_ship_info = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '1402',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'shop-usa.palaceskateboards.com',
            'Origin': 'https://shop-usa.palaceskateboards.com',
            'Referer': url_ship,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        if 'true' in str(config['settings']['captcha'].lower()):
            token = queue.get()
            log('Token used: ' + str(token),'yellow')
            payload_ship_info = {
                'utf8': '✓',
                '_method': 'patch',
                'authenticity_token': auth_token,
                'previous_step': 'contact_information',
                'step': 'shipping_method',
                'checkout[email]': config['shipping_info']['email'],
                'checkout[shipping_address][first_name]': '',
                'checkout[shipping_address][last_name]': '',
                'checkout[shipping_address][address1]': '',
                'checkout[shipping_address][address2]': '',
                'checkout[shipping_address][city]': '',
                'checkout[shipping_address][country]': '',
                'checkout[shipping_address][province]': '',
                'checkout[shipping_address][zip]': '',
                'checkout[shipping_address][phone]': '',
                'checkout[shipping_address][first_name]': config['shipping_info']['first_name'],
                'checkout[shipping_address][last_name]': config['shipping_info']['last_name'],
                'checkout[shipping_address][address1]': config['shipping_info']['address1'],
                'checkout[shipping_address][address2]': config['shipping_info']['address2'],
                'checkout[shipping_address][city]': config['shipping_info']['city'],
                'checkout[shipping_address][country]': config['shipping_info']['country'],
                'checkout[shipping_address][province]': config['shipping_info']['province'],
                'checkout[shipping_address][zip]': config['shipping_info']['zip'],
                'checkout[shipping_address][phone]': config['shipping_info']['phone'],
                'checkout[remember_me]': 'true',
                'checkout[remember_me]': '0',
                'checkout[remember_me]': '1',
                'button': '',
                'checkout[client_details][browser_width]': '1440',
                'checkout[client_details][browser_height]': '732',
                'checkout[client_details][javascript_enabled]': '1',
                'g-recaptcha-response': token
            }
        else:
            payload_ship_info = {
                'utf8': '✓',
                '_method': 'patch',
                'authenticity_token': auth_token,
                'previous_step': 'contact_information',
                'step': 'shipping_method',
                'checkout[email]': config['shipping_info']['email'],
                'checkout[shipping_address][first_name]': '',
                'checkout[shipping_address][last_name]': '',
                'checkout[shipping_address][address1]': '',
                'checkout[shipping_address][address2]': '',
                'checkout[shipping_address][city]': '',
                'checkout[shipping_address][country]': '',
                'checkout[shipping_address][province]': '',
                'checkout[shipping_address][zip]': '',
                'checkout[shipping_address][phone]': '',
                'checkout[shipping_address][first_name]': config['shipping_info']['first_name'],
                'checkout[shipping_address][last_name]': config['shipping_info']['last_name'],
                'checkout[shipping_address][address1]': config['shipping_info']['address1'],
                'checkout[shipping_address][address2]': config['shipping_info']['address2'],
                'checkout[shipping_address][city]': config['shipping_info']['city'],
                'checkout[shipping_address][country]': config['shipping_info']['country'],
                'checkout[shipping_address][province]': config['shipping_info']['province'],
                'checkout[shipping_address][zip]': config['shipping_info']['zip'],
                'checkout[shipping_address][phone]': config['shipping_info']['phone'],
                'checkout[remember_me]': 'true',
                'checkout[remember_me]': '0',
                'checkout[remember_me]': '1',
                'button': '',
                'checkout[client_details][browser_width]': '1440',
                'checkout[client_details][browser_height]': '732',
                'checkout[client_details][javascript_enabled]': '1',
            }


        # Submit Shipping info
        log('Submitting Shipping Information..','yellow')
        checkout1 = session.post(checkout0.url, data=payload_ship_info, headers=headers_ship_info, allow_redirects=True)

        # Check if we successfully submitted shipping info
        match = re.search('Return to customer information',checkout1.text)
        if match:
            log('At Shipping Method - URL: ' + checkout1.url, 'pink')

        else:
            log('Error submitting shipping information','error')
            print(checkout1.text)

        match1 = re.findall('(class=\"radio-wrapper\" data-shipping-method=\")([^\"]*)', checkout1.text)[0][1]
        log('Shipping Method: ' + match1, 'yellow')
        url_shipmethod = str(checkout0.url) + '?step=shipping_method'

        # Submit Shipping Method
        headers_ship_method = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '432',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'shop-usa.palaceskateboards.com',
            'Origin': 'https://shop-usa.palaceskateboards.com',
            'Referer': url_shipmethod,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        auth_token_method = re.findall('(name=\"authenticity_token\" value=\")([^\"]*)',checkout1.text)[0][1]
        payload_ship_method = {
            'utf8': '✓',
            '_method': 'patch',
            'authenticity_token': auth_token_method,
            'previous_step': 'shipping_method',
            'step': 'payment_method',
            'checkout[shipping_rate][id]': match1,
            'button': '',
            'checkout[client_details][browser_width]': '1440',
            'checkout[client_details][browser_height]': '732',
            'checkout[client_details][javascript_enabled]': '1',
        }

        log('Submitting Shipping Method..','yellow')
        checkout2 = session.post(checkout0.url, data=payload_ship_method, headers=headers_ship_method, allow_redirects=True)

        match = re.search('Complete order',checkout2.text)
        if match:
            log('At Payment Method - URL: ' + checkout2.url, 'pink')
        else:
            log('Error submitting shipping method','error')

        ccinfo = {
            'credit_card': {
                'number': config['card_info']['number'],
                'verification_value': config['card_info']['cvv'],
                'name': config['shipping_info']['first_name'] + ' ' + config['shipping_info']['last_name'],
                'month': int(config['card_info']['exp_month']),
                'year': int(config['card_info']['exp_year'])

            }
        }

        ccinfo_encode = json.dumps(ccinfo)
        headers_cc = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
        'Content-Type': 'application/json'
        }
        # Payment

        # elb.deposit.shopifycs.com/sessions
