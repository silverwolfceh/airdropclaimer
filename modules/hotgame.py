import requests
import datetime
import time
from .base import basetap
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://api0.herewallet.app/api/v1/user/hot/claim"

DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": "",
    "DeviceId": "fac74489-b389-4995-b300-ade9ca46f159",
    "Network": "mainnet",
    "Origin": "https://tgapp.herewallet.app",
    "Platform": "telegram",
    "Referer": "https://tgapp.herewallet.app/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Telegram-Data": "",
    "is-sbt": "false",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\", \"Microsoft Edge WebView2\";v=\"125\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}

# Body
body = {
    "game_state": {
        "refferals": 0,
        "inviter": "rokbotsxyz.tg",
        "village": None,
        "last_claim": 1715917927717436700,
        "firespace": 0,
        "boost": 11,
        "storage": 20,
        "balance": 34001
    }
}

DEFAULT_AUTH = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx.5J1KlVcsKpOWRV3h-FwSLQ_J1QlYS_5ibGBbZW_V2Q4"

class hotgame(basetap):
    def __init__(self, auth = DEFAULT_AUTH, proxy = None, headers = DEFAULT_HEADERS):
        super().__init__()
        self.auth = auth
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 20
        self.name = self.__class__.__name__
        self.last_claim = None
        self.acc_id = None
        self.valid = False
        self.update_header("Authorization", DEFAULT_AUTH)
        self.body = {
            "game_state": {
                "refferals": 0,
                "inviter": "rokbotsxyz.tg",
                "village": None,
                "last_claim": 1715917927717436700,
                "firespace": 0,
                "boost": 11,
                "storage": 20,
                "balance": 34001
            }
        }

    def storage_to_hours(self, storagelvl):
        try:
            return {
                "20" : 2,
                "21" : 3,
                "22" : 4,
                "23" : 6,
                "24" : 12,
                "25" : 24
            }[str(storagelvl)]
        except Exception as e:
            self.bprint(f"Unknown storage level {storagelvl}, Falseback to 2 hours")
            return 2

    def parse_config(self, cline):
        self.acc_id = cline["accid"]
        self.update_header("Authorization", cline["Authorization"])
        self.update_header("Telegram-Data", cline["init_data"])

    def get_account_info(self):
        if self.acc_id is None:
            self.bprint("Please add a config: accid into config.json")
        else:
            url = f"https://rpc.web4.near.page/account/game.hot.tg/view/get_user?account_id={self.acc_id}"
            try:
                res = requests.get(url, verify=False)
                data = res.json()
                new_game_state = {
                    "refferals": data['refferals'],
                    "inviter": data['inviter'],
                    "village": data['village'],
                    "last_claim": data['last_claim'],
                    "firespace": data['firespace'],
                    "boost": data['boost'],
                    "storage": data['storage'],
                    "balance": data['balance']
                }
                self.body["game_state"] = new_game_state
                self.last_claim = data['last_claim']
                self.valid = True
            except Exception as e:
                self.bprint(e)

    def ready_to_claim(self):
        if self.last_claim is None:
            self.bprint("Look like the code is wrong")
        storage_fill_time = self.storage_to_hours(self.body["game_state"]["storage"])
        storage_fill_time = storage_fill_time * 60 * 60 * 1000000000 # Convert to Nano second
        current_time = time.time_ns()
        self.wait_time = (int(self.last_claim) + int(storage_fill_time)) - current_time
        print(self.wait_time)
        if self.wait_time < 0:
            self.wait_time = int(storage_fill_time / 1000000000) + 20
            self.bprint("Time to claim, call claim function")
            return True
        else:
            self.wait_time = int(self.wait_time / 1000000000) + 20
            self.bprint(f"Not time to claim yet. Waiting {self.wait_time} seconds")
            return False

    def claim_(self):
        response = requests.post(url, headers=self.headers, json=self.body)
        print(response.json())
        pass

    def claim(self):
        self.get_account_info()
        print(self.body["game_state"])
        if self.ready_to_claim():
            self.claim_()

    


if __name__ == "__main__":
    obj = hotgame()
    obj.set_acc_id("rokbotsxyz.tg")
    obj.tap()