import requests
if __name__ == "__main__":
    from base import basetap
else:
    from .base import basetap
from datetime import datetime, timedelta, timezone
import random

DEFAULT_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Authorization": "user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22Evis%22%2C%22last_name%22%3A%22The%20Cat%22%2C%22username%22%3A%22rokbotsxyz%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&chat_instance=-1610386127424635901&chat_type=sender&start_param=6744843167&auth_date=1716819298&hash=458146b43fb6ebe52ec993f095969dcfc619474cbf43cd31cb7864356c2d9951",
    "DNT": "1",
    "Origin": "https://cell-frontend.s3.us-east-1.amazonaws.com",
    "Referer": "https://cell-frontend.s3.us-east-1.amazonaws.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "sec-ch-ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

class cellcoin(basetap):
    def __init__(self, proxy = None, headers = DEFAULT_HEADER):
        super().__init__()
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.wait_time = 20
        self.name = self.__class__.__name__
        self.energy = 0
        self.storage_to_mining_time = {
            0 : 2,
            1 : 3,
            2: 4,
        }

    def get_mine_time(self, storage_level):
        x = int(storage_level)
        return {
            0 : 2,
            1 : 3,
            2 : 4,
            3: 6,
            4: 12,
            5 : 24
        }[x]

    def get_next_wating_time(self, last_claim, storage_level):
        mining_time = self.get_mine_time(storage_level)
        last_claimed_dt = datetime.strptime(last_claim[:26] + 'Z', "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        next_claimed_dt = last_claimed_dt + timedelta(hours=mining_time)
        current_time = datetime.now(timezone.utc)
        # Calculate the waiting time in seconds
        waiting_time_seconds = (next_claimed_dt - current_time).total_seconds()
        # Ensure the waiting time is not negative
        self.wait_time = max(0, waiting_time_seconds)

    def print_waiting_time(self):
        # Convert seconds to hours and minutes
        hours, remainder = divmod(self.wait_time, 3600)
        minutes, _ = divmod(remainder, 60)
        self.bprint(f"Waiting time: {int(hours)} hours and {int(minutes)} minutes")

    def get_balance_and_remain_time(self):
        url = "https://cellcoin.org/users/session"

        try:
            response = requests.post(url, headers=self.headers)
            data = response.json()
            self.get_next_wating_time(data["cell"]["storage_fills_at"], data["cell"]["storage_level"])
            self.energy = data["cell"]["energy_amount"]
            if self.wait_time > 0:
                self.print_waiting_time()
        except Exception as e:
            self.bprint(e)


    def try_claim(self):
        url = "https://cellcoin.org/cells/claim_storage"
        try:
            response = requests.post(url, headers=self.headers)
            data = response.json()
            if int(data["cell"]["storage_balance"]) == 0:
                self.bprint("Claim success")
            self.print_balance(float(data["cell"]["balance"]))
            self.get_next_wating_time(data["cell"]["storage_fills_at"], data["cell"]["storage_level"])
            if self.wait_time > 0:
                self.print_waiting_time()
        except Exception as e:
            self.bprint(e)

    def tap(self):
        url = "https://cellcoin.org/cells/submit_clicks"

        payload = {
            "clicks_amount": random.randint(100, 300)
        }


        try:
            data = self.post_data(url, payload)
            if "cell" in data and "energy_amount" in data["cell"]:
                self.bprint("Tap success")
                self.print_balance(float(data["cell"]["balance"]))
                self.energy = data["cell"]["energy_amount"]
                self.get_next_wating_time(data["cell"]["storage_fills_at"], data["cell"]["storage_level"])
                if self.wait_time <= 0:
                    self.try_claim()
                else:
                    self.print_waiting_time()

                if self.energy <= 100:
                    self.bprint("No tap available!")
                    self.wait_time = 300
                else:
                    self.wait_time = 10

        except Exception as e:
            self.bprint(e)


    def parse_config(self, cline):
        self.update_header("Authorization", cline["Authorization"])

    def claim(self):
        self.tap()

if __name__ == "__main__":
    obj = cellcoin()
    cline = {
        "Authorization": "user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22Evis%22%2C%22last_name%22%3A%22The%20Cat%22%2C%22username%22%3A%22rokbotsxyz%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&chat_instance=-1610386127424635901&chat_type=sender&start_param=6744843167&auth_date=1716819298&hash=458146b43fb6ebe52ec993f095969dcfc619474cbf43cd31cb7864356c2d9951"
    }
    obj.parse_config(cline)
    obj.claim()

