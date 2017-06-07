#!/usr/bin/env python3

import requests
import time
import threading
import json
from classes.logger import Logger
from classes.cart import Cart
from classes.captcha import Captcha
from classes.queue import Queue
from classes.tools import Tools



if __name__ == '__main__':
    session = requests.Session()
    lock = threading.Lock()
    tools = Tools()
    config = tools.load('config/config.json')
    log = Logger().log
    q = Queue()
    cart = Cart(session, lock)

    api_key = config['key']['2captcha']
    captcha = Captcha(api_key)

    log('Initializing script..','info')
    '''
    cart.add_to_cart(['zollar','jacket','ice'],'medium')
    cart.add_to_cart(['zollar','jacket','gold'],'small')
    '''
    t1 = threading.Thread(target=cart.add_to_cart, args=(['carabiner','palace','silver'],'one size'))
    t2 = threading.Thread(target=cart.add_to_cart, args=(['carabiner','palace','orange'],'one size'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    cart.check_cart()
    # Advised to start solving 3 minutes before drop
    #captcha.harvest()
    cart.checkout()
    # Scheduler
    # Checkout
    # parse
