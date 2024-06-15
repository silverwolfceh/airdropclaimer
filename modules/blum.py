import requests
from datetime import datetime
import time
import pytz
from .base import basetap

DEFAULT_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "authority": "game-domain.blum.codes",
    "method": "POST",
    "path": "/api/v1/game/play",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJoYXNfZ3Vlc3QiOmZhbHNlLCJ0eXBlIjoiQUNDRVNTIiwiaXNzIjoiYmx1bSIsInN1YiI6ImZkMmVkOWIyLTQxYTAtNDBkZC05N2YyLTU3YjNjMzA5NjU1YSIsImV4cCI6MTcxNzY4MTUxMCwiaWF0IjoxNzE3Njc3OTEwfQ.T90sFimauS_Prg2uJUdLqyzbeYrsqIkSKuvAGiNfAQw",
    "dnt": "1",
    "origin": "https://telegram.blum.codes",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
}

UNAUTHORIZED_HDRs = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "authority": "game-domain.blum.codes",
    "method": "POST",
    "path": "/api/v1/game/play",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "dnt": "1",
    "origin": "https://telegram.blum.codes",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
}

class blump(basetap):
    def __init__(self, proxy = None, headers = DEFAULT_HEADER):
        super().__init__()
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 20
        self.name = self.__class__.__name__
        self.remain_play_pass = 0
        self.refresh_token = ""
    
    def play_game(self):
        return False
        url = "https://game-domain.blum.codes/api/v1/game/play"
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy)
            data = res.json()
            if "gameId" in data:
                gameid = data["gameId"]
                body = {
                    "gameId": gameid,
                    "points": 300000
                }
                url = "https://game-domain.blum.codes/api/v1/game/claim"
                time.sleep(31)
                res = requests.post(url, headers=self.headers, json=body, proxies=self.proxy)
        except Exception as e:
            self.bprint(e)
    
    def get_balance_info(self):
        url = "https://game-domain.blum.codes/api/v1/user/balance"
        try:
            res = requests.get(url, headers=self.headers, proxies=self.proxy)
            data = res.json()

            if "message" in data and data["message"] == "Invalid jwt token":
                self.refresh()
                return self.get_balance_info()

            if "playPasses" in data:
                self.print_balance(float(data['availableBalance']))
                self.remain_play_pass = int(data['playPasses'])
                self.bprint(f"Your playpass: {self.remain_play_pass}")
                # if self.remain_play_pass > 0:
                    # self.bprint("Start hacking game")
                    # self.play_game()
                    # return True
                    # return self.get_balance_info()
                if "farming" in data:
                    cur = int(time.time() * 1000)
                    time_difference_s = (cur - int(data["farming"]["endTime"]))/1000
                    if time_difference_s >= 0:
                        return True
                    else:
                        self.wait_time = 0 - time_difference_s
                        return False
                else:
                    url = "https://game-domain.blum.codes/api/v1/farming/start"
                    res = requests.post(url, headers=self.headers, proxies=self.proxy)
                    return self.get_balance_info()
            else:
                return True
        except Exception as e:
            self.bprint(e)
            return True

    def claim_farm(self):
        url = "https://game-domain.blum.codes/api/v1/farming/claim"
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy)
            data = res.json()
            if "availableBalance" in data:
                self.print_balance(float(data['availableBalance']))
                self.wait_time = 5
        except Exception as e:
            self.bprint(e)
        pass

    def login(self):
        data = {
            "query" : self.init_data_raw
        }
        try:
            res = requests.post("https://gateway.blum.codes/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP", headers = UNAUTHORIZED_HDRs, json = data, proxies=self.proxy)
            data = res.json()
            if "token" in data and "access" in data["token"]:
                self.update_header("authorization", "Bearer " + data["token"]["access"])
                self.refresh_token = data["token"]["refresh"]
                return True
            self.bprint("Look like blum updated API login")
            return False
        except Exception as e:
            self.bprint(e)
            return False

    def get_daily_reward(self):
        url = "https://game-domain.blum.codes/api/v1/daily-reward?offset=-420"
        if self.refresh_token == "":
            self.login()
        
        data = "offset=-420"
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy, data=data)
            if res.status_code == 200:
                self.bprint("Get daily reward success")
                return True
        except Exception as e:
            self.bprint(e)
        return False

    def refresh(self):
        if self.refresh_token == "":
            return self.login()
        else:
            data = {
                "refresh" : self.refresh_token
            }
            try:
                url = "https://gateway.blum.codes/v1/auth/refresh"
                res = requests.post(url, headers= UNAUTHORIZED_HDRs, json = data, proxies=self.proxy)
                data = res.json()
                if "access" in data:
                    self.update_header("authorization", "Bearer " + data["access"])
                    self.refresh_token = data["refresh"]
                    return True
                self.bprint("Look like blum updated API")
                return False
            except Exception as e:
                self.bprint(e)
                return False

    def parse_config(self, cline):
        self.update_header("authorization", cline["Authorization"])
        self.parse_init_data_raw(cline["init_data"])

    def claim(self):
        self.get_daily_reward()
        if self.get_balance_info():
            self.claim_farm()
            
        