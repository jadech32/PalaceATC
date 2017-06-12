import requests
from classes.logger import Logger
from time import sleep

class Captcha:

    def __init__(self, apikey):
        self.apiKey = apikey
        self.sitekey = '6LeoeSkTAAAAAA9rkZs5oS82l69OEYjKRZAiKdaF' # Default shopify sitekey
        self.url = 'shop-usa.palaceskateboards.com'

    def harvest(self, queue):
        log = Logger().log
        api_key = self.apiKey
        log('Harvesting Captcha..','info')

        s = requests.Session()

        captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(api_key, self.sitekey, self.url)).text.split('|')[1]
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(api_key, captcha_id)).text
        log("solving ref captcha...", 'yellow')
        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            sleep(1)
            recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(api_key, captcha_id)).text
        recaptcha_answer = recaptcha_answer.split('|')[1]

        log('Solved Captcha: ' + str(recaptcha_answer),'success')
        queue.put(recaptcha_answer)
