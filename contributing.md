# Getting started

1. Clone this repo
2. Create a new class in modules folder:
- Class should inherit from basetap
- Class should have parse_config and claim function implement
- Class should control its self.wait_time variable
- The file name and classname MUST be the same
3. Update the helper/data.js for your class template: classname, Field required, Field description
4. Generate example config from config helper
5. Test your class
6. Create a pull-request with evidence screenshot is a plus

Below is an example of a class: anewcoin.py

```
import requests
if __name__ == "__main__":
	from base import basetap
else:
	from .base import basetap
import pytz
import time
from datetime import datetime

DEFAULT_HEADERS = {}

class anewcoin(basetap):
	def __init__(self, auth = None, proxy = None, headers = DEFAULT_HEADERS):
		super().__init__()
		self.wait_time = 5

	def do_claim(self):
		url = "claim url"
		payload = {
			"abc" : "xyz"
		}
		try:
			res = requests.post(url, headers= self.headers, proxies=self.proxy, json=payload)
			data = res.json()
			if "balance" in data:
					self.print_balance(int(data["balance"]))
		except Exception as e:
				self.bprint(e)

	def parse_config(self, cline):
		self.parse_init_data_raw(cline['init_data'])

	def claim(self):
		# Do checking and claim, open box or all the activity here
		self.do_claim()
		# Make sure to update wait_time, it is the next time to run this object
		self.wait_time = 10
```
