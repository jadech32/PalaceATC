#!/usr/bin/env python3

import requests
import time
import threading
from classes.logger import Logger
from classes.cart import Cart
from classes.captcha import Captcha
from classes.queue import Queue


if __name__ == '__main__':
    session = requests.Session()
    lock = threading.Lock()

    log = Logger().log
    q = Queue()
    cart = Cart(session, lock)
    captcha = Captcha('070ce5ca29f5dadf76a1b2913ba0d9b7')

    log('Initializing script..','info')
    '''
    cart.add_to_cart(['zollar','jacket','ice'],'medium')
    cart.add_to_cart(['zollar','jacket','gold'],'small')
    '''
    t1 = threading.Thread(target=cart.add_to_cart, args=(['zollar','jacket','ice'],'medium'))
    t2 = threading.Thread(target=cart.add_to_cart, args=(['zollar','jacket','gold'],'large'))
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
