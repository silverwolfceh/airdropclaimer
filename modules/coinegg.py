import requests
import time
if __name__ == "__main__":
    from base import basetap
else:
    from .base import basetap

DEFAULT_HEADERS = {
    "authority": "egg-api.hivehubs.app",
    "method": "POST",
    "path": "/api/user/assets",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "cache-control": "no-cache",
    "dnt": "1",
    "origin": "https://app-coop.rovex.io",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://app-coop.rovex.io/",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "Content-Type": "application/json"
}

class coinegg(basetap):
    def __init__(self, auth = None, proxy = None, headers = DEFAULT_HEADERS):
        super().__init__()
        self.auth = None
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 5
        self.name = self.__class__.__name__
        self.token = None
        self.refresh_token = None
        self.egglist = []
    
    def parse_config(self, cline):
        self.parse_init_data_raw(cline["init_data"])
        
    def login(self):
        url = "https://egg-api.hivehubs.app/api/login/tg"
        payload = {
            "init_data": self.init_data_raw,
            "referrer": ""
        }
        data = self.post_data(url, payload)
        if data and "code" in data and data["code"] == 0:
            self.token = data["data"]["token"]["token"]
            self.refresh_token = data["data"]["token"]["refresh"]
            return True
        return False

    def get_assets(self):
        if self.token is None:
            self.login()
        url = "https://egg-api.hivehubs.app/api/user/assets"
        payload = {
            "token" : self.token
        }
        data = self.post_data(url, payload)
        if data and "code" in data and data["code"] == 0:
            egg = data["data"]["egg"]["amount"]
            usdt = data["data"]["usdt"]["amount"]
            self.cprint(f"Egg balance: {egg}")
            self.cprint(f"USDT balance: {usdt}")
    
    def get_avai_eggs(self):
        if self.token is None:
            self.login()
        url = "https://egg-api.hivehubs.app/api/scene/info"
        payload = {
            "token" : self.token
        }
        self.egglist = []
        data = self.post_data(url, payload)
        if data and "code" in data and data["code"] == 0:
            self.egglist = data["data"][0]["eggs"]
            if self.egglist is None:
                self.egglist = []
    
    def collect_eggs(self):
        if self.token is None:
            self.login()

        url = "https://egg-api.hivehubs.app/api/scene/egg/reward"
        for i in range(0, len(self.egglist)):
            egg = self.egglist[i]
            payload = {
                'token' : self.token,
                'egg_uid' : egg["uid"]
            }
            data = self.post_data(url, payload)
            try:
                if data and "code" in data and data["code"] == 0:
                    msg = f"Collected {data['data']['a_type']} with amount {data['data']['amount']}"
                    self.cprint(msg)
                    time.sleep(1)
            except Exception as e:
                self.bprint("It shouldn't here")

    def claim(self):
        self.login()
        self.get_assets()
        self.get_avai_eggs()
        self.collect_eggs()
        self.get_assets()
        self.wait_time = 10


if __name__ == "__main__":
    obj = coinegg()
    cline = {"init_data" : "query_id=AAGSXjtPAgAAAJJeO08Oad0P&user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22The%20Meoware%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22themeoware%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1718437694&hash=de21ad5c36a82792b340667718cc31c85fe8eea1e6c459fab9f6afd906385991"}
    obj.parse_config(cline)
    obj.claim()
    print(obj.wait_time)