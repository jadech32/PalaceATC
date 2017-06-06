#!/usr/bin/env python3

import requests
import time
from classes.logger import logger
from classes.cart import cart


if __name__ == '__main__':
    session = requests.Session()
    log = logger().log
    cart = cart(session)

    log('Initializing script..','info')
    cart.add_to_cart(['palace','jeans','midwash'])

    # parse
