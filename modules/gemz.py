import requests
if __name__ == "__main__":
    from base import basetap
else:
    from .base import basetap
import pytz
import time
import random
from datetime import datetime
import secrets
from urllib.parse import unquote, quote
import base64

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
    "User-Agent" : "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"
}


class gemz(basetap):
    def __init__(self, auth = None, proxy = None, headers = DEFAULT_HEADERS):
        super().__init__()
        self.auth = None
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 5
        self.name = self.__class__.__name__
        self.token = None
        self.rev = None
        self.num_queue_next = 10
        self.energy = 0

    def gen_sid_crid(self):
        random_bytes = secrets.token_bytes(6)
        base64_string = base64.b64encode(random_bytes).decode('utf-8')
        return base64_string[:9]

    def parse_config(self, cline):
        self.parse_init_data_raw(cline["init_data"])

    def loginOrCreate(self):
        user_obj = self.init_data["user"]
        tg_web_data = unquote(unquote(self.init_data_raw))
        user_data = quote(tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0])
        url = "https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.19.4/loginOrCreate"
        payload = {
            "auth" : f"auth_date={self.init_data['auth_date']}\nhash={self.init_data['hash']}\nquery_id={self.init_data['query_id']}\nuser={user_data}",
            "id" : str(user_obj["id"]),
            "sid" : self.gen_sid_crid()
        }
        data = self.post_data(url, payload)
        print(data)
        if "data" in data and "token" in data["data"]:
            self.token = data["data"]["token"]
            self.rev = int(data["data"]["rev"])
            self.print_balance(int(data["data"]["state"]["balance"]))
            self.energy = int(data["data"]["state"]["energy"])
            self.cprint(f"Remain energy: {self.energy}")
            self.bprint("Login success")
        else:
            self.bprint("Failed to login, may be code wrong")
            self.wait_time = 3600

    def generate_tap_queue(self, delaymin = 75, delaymax = 150, num_queue = None):
        if num_queue is None:
            num_queue = random.randint(50, 100)
        tap_queue = []
        cur_epoch = int(time.time() * 1000)
        for i in range(0, num_queue):
            this_delay = random.randint(delaymin, delaymax)
            cur_epoch = cur_epoch + this_delay
            atap = {"fn": "tap", "async": False, "meta": {"now": cur_epoch}}
            tap_queue.append(atap)
        return tap_queue
    
    def get_full_energy(self):
        url = "https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.19.5/replicate"
        payload = {
            "abTestsDynamicConfig": {
                "0002_invite_drawer": {"active": True, "rollOut": 1},
                "0003_invite_url": {"active": True, "rollOut": 1},
                "0004_invite_copy": {"active": True, "rollOut": 1},
                "0010_localization": {"active": True, "rollOut": 1},
                "0006_daily_reward": {"active": False, "rollOut": 0},
                "0011_earn_page_buttons": {"active": True, "rollOut": 1},
                "0005_invite_message": {"active": True, "rollOut": 1},
                "0008_retention_with_points": {"active": True, "rollOut": 1},
                "0018_earn_page_button_2_friends": {"active": True, "rollOut": 1},
                "0012_rewards_summary": {"active": True, "rollOut": 1},
                "0022_localization": {"active": True, "rollOut": 1},
                "0023_earn_page_button_connect_wallet": {"active": True, "rollOut": 1},
                "0016_throttling": {"active": True, "rollOut": 1},
                "0024_rewards_summary2": {"active": True, "rollOut": 1},
                "0016_throttling_v2": {"active": True, "rollOut": 1},
                "0014_gift_airdrop": {"active": True, "rollOut": 1},
                "0007_game_preview": {"active": True, "rollOut": 1}
            },
            "queue": [
                {"fn": "buyBuff", "async": False, "args": {"buff": "FullEnergy"}, "meta": {"now": int(time.time() * 1000)}}
            ],
            "rev": self.rev,
            "requestedProfileIds": [],
            "consistentFetchIds": [],
            "sid": self.gen_sid_crid(),
            "clientRandomSeed": 0,
            "crqid": self.gen_sid_crid(),
            "id": str(self.init_data["user"]["id"]),
            "auth": self.token
        }

        data = self.post_data(url, payload)
        print(data)
        if "data" in data and "rev" in data["data"]:
            self.rev = data["data"]["rev"]
            self.bprint("Buy boost OK, let login again to refresh data")
            self.loginOrCreate()
            return True
        else:
            self.bprint("Buy bosst failed")
            return False

    def tap(self):
        if self.token is None:
            self.loginOrCreate()

        if self.energy <= 10:
            self.wait_time = 3600
            return None

        url = "https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.19.4/replicate"
        payload = {
            "abTestsDynamicConfig": {
            "0002_invite_drawer": {"active": True, "rollOut": 1},
            "0003_invite_url": {"active": True, "rollOut": 1},
            "0004_invite_copy": {"active": True, "rollOut": 1},
            "0010_localization": {"active": True, "rollOut": 1},
            "0006_daily_reward": {"active": False, "rollOut": 0},
            "0011_earn_page_buttons": {"active": True, "rollOut": 1},
            "0005_invite_message": {"active": True, "rollOut": 1},
            "0008_retention_with_points": {"active": True, "rollOut": 1},
            "0018_earn_page_button_2_friends": {"active": True, "rollOut": 1},
            "0012_rewards_summary": {"active": True, "rollOut": 1},
            "0022_localization": {"active": True, "rollOut": 1},
            "0023_earn_page_button_connect_wallet": {"active": True, "rollOut": 1},
            "0016_throttling": {"active": True, "rollOut": 1},
            "0024_rewards_summary2": {"active": True, "rollOut": 1},
            "0016_throttling_v2": {"active": True, "rollOut": 1},
            "0014_gift_airdrop": {"active": True, "rollOut": 1},
            "0007_game_preview": {"active": True, "rollOut": 1}
            },
            "queue": self.generate_tap_queue(2, 5, self.num_queue_next),
            "rev": self.rev,
            "requestedProfileIds": [],
            "consistentFetchIds": [],
            "sid": self.gen_sid_crid(),
            "clientRandomSeed": 0,
            "crqid": self.gen_sid_crid(),
            "id": str(self.init_data["user"]["id"]),
            "auth": self.token
        }
        self.bprint(f"Tap {len(payload['queue'])} times this round")
        data = self.post_data(url, payload)
        print(data)
        if "data" in data and "rev" in data["data"]:
            self.rev = data["data"]["rev"]
            self.energy = self.energy - len(payload['queue'])
            self.num_queue_next = random.randint(50, 100) if self.energy > 100 else self.energy
            if self.num_queue_next <= 0:
                self.bprint("No more tap")
                if self.get_full_energy():
                    return 0
                else:
                    self.wait_time = 3600
                    return None
            return len(payload['queue'])
        elif "code" in data and data["code"] == "session_desync_error":
            self.bprint("Lost session sync, re-login")
            self.loginOrCreate()
            return 0
        return 0

    def claim(self):
        self.loginOrCreate()
        ret = self.tap()
        while ret is not None:
            if self.stopped:
                break
            ret = self.tap()
            time.sleep(1)
        
        

if __name__ == "__main__":
    obj = gemz()
    cline = {"init_data" : "query_id=AAGSXjtPAgAAAJJeO093-fG5&user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22The%20Meoware%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22themeoware%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1718807519&hash=3aacea7eb8aca0f9f7be39de577697adcf21a9ddfa0cdb93170da2a175e1d624"}
    obj.parse_config(cline)
    obj.loginOrCreate()
    obj.get_full_energy()