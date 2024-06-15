import requests
import datetime
import time
from .base import basetap

url = "https://api.hamsterkombat.io/clicker/tap"

DEFAULT_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "authorization": "Bearer 17135328889144GZkVJpJhxCCkBjffo6FNgBr2gM4pQTg8TU4ADhWjpJSTHI127AqcYfiDXS3VtgA5624258194",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://hamsterkombat.io",
    "priority": "u=1, i",
    "referer": "https://hamsterkombat.io/",
    "sec-ch-ua": "\"Chromium\";v=\"124\", \"Microsoft Edge\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
}

DEFAULT_AUTH = "Bearer 17135328889144GZkVJpJhxCCkBjffo6FNgBr2gM4pQTg8TU4ADhWjpJSTHI127AqcYfiDXS3VtgA5624258194"

class hamster(basetap):
    def __init__(self, auth = DEFAULT_AUTH, proxy = None, headers = DEFAULT_HEADERS):
        super().__init__()
        self.auth = auth
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 20
        self.name = self.__class__.__name__
        self.last_remain = 1

    def parse_config(self, cline):
        self.update_header("authorization", cline["authorization"])

    def get_balance_info(self):
        url = "https://api.hamsterkombat.io/clicker/sync"
        data = self.post_data(url, None)
        if "clickerUser" in data:
            self.last_remain = data["clickerUser"]["availableTaps"]

    def boost_if_ok(self):
        url = "https://api.hamsterkombat.io/clicker/boosts-for-buy"
        data = self.post_data(url, None)
        if "boostsForBuy" in data and len(data["boostsForBuy"]) >= 3:
            boostfulltap = data["boostsForBuy"][2]
            self.bprint(f"Available boost in: {boostfulltap['cooldownSeconds']} seconds")
            if int(boostfulltap["cooldownSeconds"]) == 0:
                url = "https://api.hamsterkombat.io/clicker/buy-boost"
                payload = {
                    "boostId" : "BoostFullAvailableTaps",
                    "timestamp" : int(datetime.datetime.now().timestamp())
                }
                data = self.post_data(url, payload)
                if "clickerUser" in data:
                    self.bprint("Active boost OK")
                else:
                    self.bprint("Active boost failed")

    def claim(self):
        self.get_balance_info()
        current_time = datetime.datetime.now()
        current_timestamp = int(current_time.timestamp())
        data = {
            "count": self.last_remain,
            "availableTaps": 0,
            "timestamp": current_timestamp
        }
        try:
            response = requests.post(url, headers=self.headers, json=data, proxies=self.proxy)
            data = response.json()
            self.print_balance(data['clickerUser']['balanceCoins'])
        except Exception as e:
            self.bprint(e)

        self.boost_if_ok()
