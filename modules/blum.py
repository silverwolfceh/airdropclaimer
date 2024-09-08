import requests
from datetime import datetime
import time
import sys
import random
import pytz
if __name__ == "__main__":
    from base import basetap
else:
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
        # return False
        url = "https://game-domain.blum.codes/api/v1/game/play"
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy)
            data = res.json()
            if "gameId" in data:
                gameid = data["gameId"]
                body = {
                    "gameId": gameid,
                    "points": random.randint(150, 200)
                }
                url = "https://game-domain.blum.codes/api/v1/game/claim"
                self.animated_sleeping(31)
                res = requests.post(url, headers=self.headers, json=body, proxies=self.proxy)
                if res.status_code == 200:
                    self.bprint(f"Success claim : {body['points']}")
                
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
            res = requests.post("https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP", headers = UNAUTHORIZED_HDRs, json = data, proxies=self.proxy)
            data = res.json()
            if "token" in data and "access" in data["token"]:
                self.bprint("Login success")
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

    def animated_sleeping(self, duration=5, interval=0.5):
        cursor = ['|', '/', '-', '\\']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            sys.stdout.write("\r" + cursor[i % len(cursor)])
            sys.stdout.flush()
            i += 1
            time.sleep(interval)
        # sys.stdout.write("\rDone!\n")

    def claim(self):
        self.login()
        self.get_daily_reward()
        self.get_balance_info()
        self.claim_farm()
        while self.remain_play_pass > 0:
            self.play_game()
            self.get_balance_info()
        # self.play_game()
        # self.get_daily_reward()
        # if self.get_balance_info():
            # self.claim_farm()
            
if __name__ == "__main__":
    obj = blump()
    cline = {
        "Authorization" : "",
        "init_data": "query_id=AAGSXjtPAgAAAJJeO08WZZ_U&user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22The%20Meoware%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22themeoware%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1718025593&hash=1d1a42b8d53f1b9c3575eb44ebad2a2ecd99460bbb3e55ca6d197e820f2d2717",    }
    obj.parse_config(cline)
    obj.claim()