import requests
from datetime import datetime
import time
import pytz
from .base import basetap

DEFAULT_HEADER = {
    "authority": "cexp.cex.io",
    "method": "POST",
    "path": "/api/claimTaps",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "dnt": "1",
    "origin": "https://cexp.cex.io",
    "priority": "u=1, i",
    "referer": "https://cexp.cex.io/",
    "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
}

class cexio(basetap):
    def __init__(self, proxy = None, headers = DEFAULT_HEADER):
        super().__init__()
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 20
        self.name = self.__class__.__name__
        self.farm_reward = 0
        self.children_reward = 0
        self.next_farm_collect_time = 0
        

    def claim_children_reward(self):
        url = "https://cexp.cex.io/api/getChildren"

        try:
            response = requests.post(url, headers=self.headers, json = self.bodynormal)
            data = response.json()

            self.children_reward = float(data["data"]["totalRewardsToClaim"])
            if self.children_reward > 0:
                url = "https://cexp.cex.io/api/claimFromChildren"
                response = requests.post(url, headers=self.headers, json= self.bodynormal)
                data = response.json()
                if data["status"] == "ok":
                    self.bprint("Claim children reward ok")
        except Exception as e:
            self.bprint(e)
            return 0

    def update_farm_collect_time(self, start_time, duration):
        datetime_obj = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        datetime_obj = datetime_obj.replace(tzinfo=pytz.UTC)
        # Convert to epoch seconds
        epoch_seconds = int(datetime_obj.timestamp())
        self.next_farm_collect_time = epoch_seconds + int(duration) + 20 # Add 20s for backup

    def is_ready_to_collect_farm(self):
        current_epoch_seconds = int(time.time())
        return current_epoch_seconds >= self.next_farm_collect_time


    def get_balance_and_remain(self):
        url = "https://cexp.cex.io/api/getUserInfo"

        try:
            response = requests.post(url, headers=self.headers, json = self.bodynormal)
            data = response.json()
            self.print_balance(float(data["data"]["balance"]))
            self.farm_reward = float(data["data"]["farmReward"])
            try:
                self.update_farm_collect_time(data["data"]["farmStartedAt"], data["data"]["miningEraIntervalInSeconds"])
            except Exception as e:
                self.bprint(e)
            return data["data"]["availableTaps"]
        except Exception as e:
            self.bprint(e)
            return 0
    
    def claim_farm_and_start_farm(self):
        url = "https://cexp.cex.io/api/claimFarm"
    
        if not self.is_ready_to_collect_farm():
            return

        try:
            response = requests.post(url, headers=self.headers, json= self.bodynormal)
            data = response.json()
            print(data)
            if data["status"] == "ok" and "claimedBalance" in data["data"]:
                self.bprint("Claim farm ok")
                self.farm_reward = 0
                url = "https://cexp.cex.io/api/startFarm"
                response = requests.post(url, headers=self.headers, json = self.bodynormal)
                data = response.json()
                if data["status"] == "ok" and "farmStartedAt" in data["data"]:
                    self.bprint("Re-start farm success")
            elif data["status"] == "error" and "reason" in data["data"] and data["data"]["reason"] == "Farm is not started":
                url = "https://cexp.cex.io/api/startFarm"
                response = requests.post(url, headers=self.headers, json = self.bodynormal)
                data = response.json()
                if data["status"] == "ok" and "farmStartedAt" in data["data"]:
                    self.bprint("Re-start farm success")

        except Exception as e:
            self.bprint(e)
            return 0

    def parse_config(self, cline):
        self.parse_init_data_raw(cline["init_data"])
        self.bodynormal = {
            "devAuthData": self.init_data["user"]["id"],
            "authData": self.init_data_raw,
            "platform": "android",
            "data": {}
        }
        self.bodytap = {
            "devAuthData": self.init_data["user"]["id"],
            "authData": self.init_data_raw,
            "data": {"taps": 0}
        }

    def try_claim(self, tapnum = 1):
        url = "https://cexp.cex.io/api/claimTaps"

        body = self.bodytap
        body["data"]["taps"] = int(tapnum)

        response = requests.post(url, headers=self.headers, json=body)

    
    def claim(self):
        if not self.is_init_data_ready():
            self.bprint("Init data is required, please check config.json")
        else:
            tapnum = self.get_balance_and_remain()
            self.claim_children_reward()
            self.claim_farm_and_start_farm()
            if int(tapnum) > 0:
                self.try_claim(tapnum)
            else:
                self.bprint(f"No tap available, waiting {self.wait_time} seconds")