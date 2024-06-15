import requests
from .base import basetap
import pytz
import time
from datetime import datetime

DEFAULT_HEADERS = {
    "authority": "tg-bot-tap.laborx.io",
    "method": "POST",
    "path": "/api/v1/auth/validate-init",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "cache-control": "no-cache",
    "dnt": "1",
    "origin": "https://tg-tap-miniapp.laborx.io",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://tg-tap-miniapp.laborx.io/",
    "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Content-Type": "text/plain;charset=UTF-8",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
}


class timeframe(basetap):
    def __init__(self, auth = None, proxy = None, headers = DEFAULT_HEADERS):
        super().__init__()
        self.auth = None
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 5
        self.name = self.__class__.__name__
        self.start_time = None
        self.duration = 0

    def parse_config(self, cline):
        self.parse_init_data_raw(cline["init_data"])

    def get_token(self):
        self.auth = None
        url = "https://tg-bot-tap.laborx.io/api/v1/auth/validate-init"
        try:
            res = requests.post(url, headers= self.headers, data= self.init_data_raw, proxies=self.proxy)
            data = res.json()
            self.auth = data["token"]
            self.headers["Authorization"] = f"Bearer {self.auth}"
            return self.auth
        except Exception as e:
            self.bprint(e)
            return None

    def calc_remain_time(self):
        datetime_obj = datetime.strptime(self.start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        datetime_obj = datetime_obj.replace(tzinfo=pytz.UTC)
        # Convert to epoch seconds
        epoch_seconds = int(datetime_obj.timestamp())
        next_farm_ready = epoch_seconds + int(self.duration) + 20 # Add 20s for backup
        current_epoch_seconds = int(time.time())
        return (current_epoch_seconds - next_farm_ready)

    def get_info(self):
        url = "https://tg-bot-tap.laborx.io/api/v1/farming/info"
        if self.auth is None and self.get_token() is None:
            self.bprint("Failed to get token, may be code change")
        else:
            try:
                res = requests.get(url, headers=self.headers, proxies=self.proxy)
                data = res.json()
                self.print_balance(float(data['balance']))
                self.start_time = data['activeFarmingStartedAt']
                self.duration = data['farmingDurationInSec']
            except Exception as e:
                self.bprint(e)

    def claim(self):
        url = "https://tg-bot-tap.laborx.io/api/v1/farming/finish"
        self.get_info()
        remain_time = self.calc_remain_time()
        if remain_time >= 0:
            try:
                res = requests.post(url, headers=self.headers, proxies=self.proxy, json={})
                data = res.json()
                if "error" in data:
                    self.bprint("Calculation is wrong")
                else:
                    self.print_balance(data['balance'])
                    self.wait_time = self.duration
                    self.start_farm()
            except Exception as e:
                self.bprint("Failed to claim")
                self.bprint(e)
        else:
            self.bprint("Not time to claim yet")
            self.wait_time = 0 - remain_time

    def start_farm(self):
        url = "https://tg-bot-tap.laborx.io/api/v1/farming/start"
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy, json={})
            data = res.json()
            if "activeFarmingStartedAt" in data and len(data["activeFarmingStartedAt"]) > 10:
                return True
            else:
                self.bprint(f"Start farm failed, {data}")
                return False
        except Exception as e:
            self.bprint(f"Start farm failed, {e}")
            return False


if __name__ == "__main__":
    obj = timeframe()
    cline = {"init_data" : "query_id=AAGSXjtPAgAAAJJeO086jbG9&user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22The%20Meoware%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22themeoware%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1718197736&hash=22bdb7867b605c1f3548ff34927505220cdeb211974ef3ac15811646ff5b9ea7"}
    obj.parse_config(cline)
    obj.claim()
    print(obj.wait_time)
        