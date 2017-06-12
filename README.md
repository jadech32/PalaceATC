An easy to use script made for Palace Skateboards store. Project under development.

![](http://i.imgur.com/IMWZDdx.gif)

## Installation
- Clone or download the repo
- Change values in ```config.example.json``` then rename to ```config.json```.
- Install the requirements (done once per download)
- ```pip install requirements.txt```
- Run ```main.py```

### Adding Items
- Currently the only way to add items is to modify the threads in ```main.py```
- Follow the format in ```main.py```, only change arguments in ```args=()``` of each thread accordingly.

### Configuration settings
- ```captcha``` must be set to ```false``` as it does not work yet.
- ```retries``` is the amount of times the script retries finding the product before exiting program.
- ```polling-rate``` is the delay in between each retry / find attempt in seconds. Keep in mind that shopify gives out soft bans for too many polls.
- If you wish to checkout via your browser, set either ```EU``` or ```US``` in ```browser``` to ```true```, but not both. If you want to check out via requests (not working yet), set both to ```false```


## Issues
- Assumes that you are adding something that is not out of stock (i.e. new items). Script will terminate if there are out of stock items in your cart.
- Captcha support currently broken.
- Multiple sizes per thread / item currently not yet supported.

## Features / TODO

- [x] Add to cart
- [x] Multiple Items per cart
- [ ] Proxy support
- [ ] Checkout
- [x] Queue support
- [ ] Negative Keywords
- [ ] Scheduling

## License
```
Copyright 2017 Jade Chunnananda

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
