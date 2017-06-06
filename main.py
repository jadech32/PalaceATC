#!/usr/bin/env python3

import requests
import time
import threading
from classes.logger import logger
from classes.cart import cart


if __name__ == '__main__':
    session = requests.Session()
    log = logger().log
    lock = threading.Lock()
    cart = cart(session, lock)

    log('Initializing script..','info')
    t1 = threading.Thread(target=cart.add_to_cart, args=(['zollar','jacket','ice'],'medium'))
    t2 = threading.Thread(target=cart.add_to_cart, args=(['zollar','jacket','gold'],'small'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    cart.check_cart()

    # parse
