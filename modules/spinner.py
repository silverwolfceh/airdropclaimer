import requests
if __name__ == "__main__":
    from base import basetap
else:
    from .base import basetap
import pytz
import time
from datetime import datetime
import random


DEFAULT_HEADERS = {
    "authority": "api.timboo.pro",
    "method": "POST",
    "path": "/get_data",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "cache-control": "no-cache",
    "dnt": "1",
    "origin": "https://spinner.timboo.pro",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://spinner.timboo.pro/",
    "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Content-Type": "application/json"
}

class spinner(basetap):
    def __init__(self, auth = None, proxy = None, headers = DEFAULT_HEADERS):
        super().__init__()
        self.auth = None
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 5
        self.name = self.__class__.__name__
        self.end_time = None
        self.is_broken = False
        self.boxes = []
        self.remain_hp = 0
        self.body = {"initData" : ""}

    def parse_config(self, cline):
        self.parse_init_data_raw(cline['init_data'])
        self.body["initData"] = self.init_data_raw

    def get_info(self):
        url = "https://back.timboo.pro/api/init-data"
        try:
            res = requests.post(url, headers= self.headers, proxies=self.proxy, json=self.body)
            data = res.json()
            if "message" in data and "initData" in data:
                thespinner = data["initData"]["spinners"][0]
                self.is_broken = thespinner["isBroken"]
                self.end_time = thespinner["endRepairTime"]
                self.remain_hp = int(thespinner["hp"])
                self.spinner_id = thespinner["id"]
                self.print_balance(float(data["initData"]["user"]["balance"]))
                self.calculate_wait_time()
                return True
            else:
                self.bprint("Please check the code, get info failed")
        except Exception as e:
            self.bprint(e)
        return False
    
    def fix_spinner(self):
        url = "https://back.timboo.pro/api/repair-spinner"
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy, json=self.body)
            data = res.json()
            if "message" in data and data["message"] == "Data received successfully.":
                self.bprint("Repair spinner OK")
                return
        except Exception as e:
            self.bprint(e)
        self.bprint("Repair spinner failed")

    def calculate_wait_time(self):
        if self.end_time is None:
            self.wait_time = 0
            return
        datetime_obj = datetime.strptime(self.end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        datetime_obj = datetime_obj.replace(tzinfo=pytz.UTC)
        # Convert to epoch seconds
        end_time_epoch = int(datetime_obj.timestamp())
        current_epoch_seconds = int(time.time())
        if current_epoch_seconds > end_time_epoch:
            self.wait_time = 5
        else:
            self.wait_time = end_time_epoch - current_epoch_seconds

    def is_box_ready_to_open(self, boxopentime):
        dt = datetime.strptime(boxopentime, '%a, %d %b %Y %H:%M:%S %Z')
        # Convert to epoch seconds
        epoch_seconds = int(time.mktime(dt.timetuple()))
        current_epoch_seconds = int(time.time())
        delta_seconds = current_epoch_seconds - epoch_seconds
        one_day_seconds = 24*60*60
        if delta_seconds > one_day_seconds:
            return True
        return False
    
    def open_daily_box(self):
        self.check_daily_box()
        url = "https://api.timboo.pro/open_box"
        payload = {
            "initData" : self.init_data_raw,
            "boxId" : None
        }
        
        for b in self.boxes:
            try:
                payload["boxId"] = b
                res = requests.post(url, headers=self.headers, proxies=self.proxy, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    if "reward_text" in data:
                        self.bprint(f"Open the box#{b} OK. {data['reward_text']}")
                    else:
                        self.bprint(f"Open the box#{b} OK. ")
                    self.boxes.remove(b)
                else:
                    self.bprint(f"Failed to the box#{b}. Maybe it is already openned ")
            except Exception as e:
                self.bprint(f"Failed to open Box#{b}")
                self.bprint(e)

    def check_daily_box(self):
        self.boxes = []
        url = "https://api.timboo.pro/get_data"
        try:
            res = requests.post(url, proxies=self.proxy, headers=self.headers, json=self.body)
            data = res.json()
            print(data)
            if "boxes" in data:
                for i in range(0, len(data["boxes"])):
                    
                    if self.is_box_ready_to_open(data["boxes"][i]["open_time"]):
                        self.boxes.append(data["boxes"][i]["id"])
            self.bprint(f"Found {len(self.boxes)} boxes.")
        except Exception as e:
            self.bprint(e)

    def claim_spinner(self):
        url = "https://back.timboo.pro/api/upd-data"
        claim_point = random.randint(10, 20)
        if self.remain_hp <= 20:
            claim_point = self.remain_hp

        payload = {
            "initData" : self.init_data_raw,
            "data" : {
                "clicks" : claim_point,
                "isClose" : None
            }
        }
        try:
            res = requests.post(url, json=payload, proxies=self.proxy, headers=self.headers)
            data = res.json()
            if "updateData" in data and data["updateData"]:
                self.bprint("Claim successful")
                time.sleep(5)
                self.remain_hp = self.remain_hp - claim_point
                if self.remain_hp > 0:
                    self.claim_spinner()
                else:
                    self.fix_spinner()
                    self.get_info()
            else:
                self.wait_time = 5
                self.bprint("Try claim again in 5 seconds")
                self.get_info()
        except Exception as e:
            self.bprint(e)
            self.bprint("Error happen")
    
    def try_upgrade(self):
        url = "https://back.timboo.pro/api/upgrade-spinner"
        payload = {
            "initData" : self.init_data_raw,
            "spinnerId" : self.spinner_id
        }
        try:
            res = requests.post(url, headers= self.headers, json=payload, proxies=self.proxy)
            if res.status_code == 200:
                data = res.json()
                if "message" in data and data["message"] == "The spinner is upgraded.":
                    self.bprint("Upgrade spinner successfully")
                    return True
                else:
                    self.bprint("Failed to upgrade spinner ")
            else:
                self.bprint(f"Failed to upgrade spinner, error: {res.status_code}")
        except Exception as e:
            self.bprint(f"Failed to upgrade spinner, error: {e}")
        return False

    def claim(self):
        # obj.open_daily_box()
        self.get_info()
        while self.try_upgrade():
            time.sleep(1)
        self.fix_spinner()
        if self.wait_time <= 0:
            self.claim_spinner()
        
if __name__ == "__main__":
    obj = spinner()
    cline = {"init_data" : "query_id=AAGSXjtPAgAAAJJeO09uAAJM&user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22The%20Meoware%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22themeoware%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1718286885&hash=1c4c4f59154651ed2c0784804a61b9decaf987f4bec60c7ad13f511f45e957ab"}
    obj.parse_config(cline)
    obj.claim()