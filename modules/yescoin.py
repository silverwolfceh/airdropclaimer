import requests
import time
from .base import basetap

DEFAULT_HDRS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://www.yescoin.gold",
    "priority": "u=1, i",
    "referer": "https://www.yescoin.gold/",
    "sec-ch-ua": "\"Chromium\";v=\"124\", \"Microsoft Edge\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI1NjI0MjU4MTk0IiwiY2hhdElkIjoiNTYyNDI1ODE5NCIsImlhdCI6MTcxNjAxNDAyNiwiZXhwIjoxNzE4NjA2MDI2LCJyb2xlQXV0aG9yaXplcyI6W10sInVzZXJJZCI6MTc4MTYwMDE1NzY2NTUxMzQ3Mn0.lIzwptF434dMYW3x72AJQb7cfcKUCevn62K0RJKey4DJPeiXGItoaTr5T9Q88NJN0Y1AI7nIh5noJf8y2SIwgQ",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
}
DEFAULT_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI1NjI0MjU4MTk0IiwiY2hhdElkIjoiNTYyNDI1ODE5NCIsImlhdCI6MTcxNjAxNDAyNiwiZXhwIjoxNzE4NjA2MDI2LCJyb2xlQXV0aG9yaXplcyI6W10sInVzZXJJZCI6MTc4MTYwMDE1NzY2NTUxMzQ3Mn0.lIzwptF434dMYW3x72AJQb7cfcKUCevn62K0RJKey4DJPeiXGItoaTr5T9Q88NJN0Y1AI7nIh5noJf8y2SIwgQ"

class yescoin(basetap):
    def __init__(self, token = DEFAULT_TOKEN, proxy = None, headers = DEFAULT_HDRS):
        super().__init__()
        self.token = token
        self.proxy = proxy
        self.headers = headers
        self.headers["token"] = self.token
        self.stopped = False
        self.name = self.__class__.__name__

    def get_remain_coin(self):
        url = "https://api.yescoin.gold/game/getGameInfo"
        try:
            res = requests.get(url, headers=self.headers, proxies=self.proxy)
            if res.status_code == 200:
                data = res.json()
                # print(f"{self.name}: {data}")
                return int(int(data["data"]["coinPoolLeftCount"]) / 10)
        except Exception as e:
            self.bprint(e)
        return 0
    
    
    def collect_coin(self, numcollect):
        url = "https://api.yescoin.gold/game/collectCoin"
        try:
            res = requests.post(url, headers=self.headers, data=str(numcollect), proxies=self.proxy)
            # print(f"{self.name}: {res.json()}")
        except Exception as e:
            self.bprint(e)

    def get_boost_info(self):
        url = "https://api.yescoin.gold/build/getAccountBuildInfo"
        try:
            res = requests.get(url, headers=self.headers, proxies=self.proxy)
            data = res.json()
            if "message" in data and data["message"] == "Success":
                return data
        except Exception as e:
            self.bprint(e)
        return None

    def boost_full_energy(self):
        data = self.get_boost_info()
        if data and int(data["data"]["coinPoolLeftRecoveryCount"]) > 0:
            url = "https://api.yescoin.gold/game/recoverCoinPool"
            try:
                res = requests.post(url, headers=self.headers, proxies=self.proxy)
                data = res.json()
                if "message" in data and data["message"] == "Success":
                    self.bprint("Boost full recovery success")
                    return True
            except Exception as e:
                self.bprint(e)
        return False

    def boost_special_box(self):
        data = self.get_boost_info()
        if data and int(data["data"]["specialBoxLeftRecoveryCount"]) > 0:
            url = "https://api.yescoin.gold/game/recoverSpecialBox"
            try:
                res = requests.post(url, headers=self.headers, proxies=self.proxy)
                data = res.json()
                if "message" in data and data["message"] == "Success":
                    self.bprint("Boost special recovery success")
                    time.sleep(10)
                    payload = {
                        "boxType" : 2,
                        "coinCount" : 200
                    }
                    url = "https://api.yescoin.gold/game/collectSpecialBoxCoin"
                    res = requests.post(url, headers=self.headers, proxies=self.proxy, json=payload)
                    return True
            except Exception as e:
                self.bprint(e)
        return False
    
    def wait_time_calculate(self, timestart):
        cur = int(time.time())
        if cur > timestart:
            self.wait_time = 1
            return True
        else:
            self.wait_time = timestart - cur
            return False

    def monitor_special_box(self):
        url = "https://api.yescoin.gold/game/getSpecialBoxInfo"
        try:
            res = requests.get(url, headers=self.headers, proxies=self.proxy)
            data = res.json()
            if "message" in data and data["message"] == "Success":
                try:
                    if data["data"]["autoBox"]:
                        self.bprint("Auto box available")
                        if self.wait_time_calculate(data["data"]["autoBox"]["startTime"]):
                            payload = {
                                "boxType" : data["data"]["autoBox"]["boxType"],
                                "coinCount" : data["data"]["autoBox"]["specialBoxTotalCount"]
                            }
                            url = "https://api.yescoin.gold/game/collectSpecialBoxCoin"
                            res = requests.post(url, headers=self.headers, proxies=self.proxy, json=payload)
                            data = res.json()
                            self.bprint(data)
                    else:
                        self.bprint("No autobox found")
                except Exception as e:
                    self.bprint(e)

                try:
                    if data["data"]["recoveryBox"]:
                        revbox = data["data"]["recoveryBox"]
                        payload = {
                                "boxType" : revbox["boxType"],
                                "coinCount" : revbox["specialBoxTotalCount"]
                        }
                        url = "https://api.yescoin.gold/game/collectSpecialBoxCoin"
                        res = requests.post(url, headers=self.headers, proxies=self.proxy, json=payload)
                        data = res.json()
                        self.bprint(data)
                    else:
                        self.bprint("No recovery box found")
                except Exception as e:
                    self.bprint(e)
        except Exception as e:
            self.bprint(e)
        return None

    def get_info(self):
        url = "https://api.yescoin.gold/account/getAccountInfo"
        try:
            res = requests.get(url, headers = self.headers, proxies=self.proxy)
            self.print_balance(res.json()['data']['currentAmount'])
            # print(f"{self.name}: Account balance {res.json()['data']['currentAmount']}")
        except Exception as e:
            self.bprint(e)

    def claim(self):
        self.wait_time = 5
        self.monitor_special_box()
        remain_coin = self.get_remain_coin()
        self.collect_coin(remain_coin)
        self.get_info()
        if self.boost_full_energy():
            remain_coin = self.get_remain_coin()
            self.collect_coin(remain_coin)
            self.get_info()
        if self.boost_special_box():
            self.get_info()
        

    def parse_config(self, cline):
        self.update_header("token", cline["token"])