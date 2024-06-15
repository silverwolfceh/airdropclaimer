import requests
import time
import random
import string
from urllib.parse import unquote
from .base import basetap

# Define the URL and the headers
url = "https://api-gw-tg.memefi.club/graphql"
DEFAULT_HEADERS = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://tg-app.memefi.club',
        'Referer': 'https://tg-app.memefi.club/',
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-mobile': '?1',
        'Sec-Ch-Ua-platform': '"Android"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
}
# Define the JSON body
QUERY_LOGIN = """mutation MutationTelegramUserLogin($webAppData: TelegramWebAppDataInput!) {
            telegramUserLogin(webAppData: $webAppData) {
                access_token
                __typename
            }
        }"""

QUERY_USER = """
        query QueryTelegramUserMe {
          telegramUserMe {
            firstName
            lastName
            telegramId
            username
            referralCode
            isDailyRewardClaimed
            referral {
              username
              lastName
              firstName
              bossLevel
              coinsAmount
              __typename
            }
            isReferralInitialJoinBonusAvailable
            league
            leagueIsOverTop10k
            leaguePosition
            _id
            __typename
          }
        }
        """

QUERY_GAME_CONFIG = """
query QUERY_GAME_CONFIG {
  telegramGameGetConfig {
    ...FragmentBossFightConfig
    __typename
  }
}

fragment FragmentBossFightConfig on TelegramGameConfigOutput {
  _id
  coinsAmount
  currentEnergy
  maxEnergy
  weaponLevel
  energyLimitLevel
  energyRechargeLevel
  tapBotLevel
  currentBoss {
    _id
    level
    currentHealth
    maxHealth
    __typename
  }
  freeBoosts {
    _id
    currentTurboAmount
    maxTurboAmount
    turboLastActivatedAt
    turboAmountLastRechargeDate
    currentRefillEnergyAmount
    maxRefillEnergyAmount
    refillEnergyLastActivatedAt
    refillEnergyAmountLastRechargeDate
    __typename
  }
  bonusLeaderDamageEndAt
  bonusLeaderDamageStartAt
  bonusLeaderDamageMultiplier
  nonce
  __typename
}
"""


class memefi(basetap):
    def __init__(self, auth = "", proxy = None, headers = DEFAULT_HEADERS):
        super().__init__()
        self.auth = auth
        self.proxy = proxy
        self.headers = headers
        self.access_token = None
        self.stopped = False
        self.wait_time = 10
        self.remain_boost = 0
        self.name = self.__class__.__name__
        self.claimbody = {
            "operationName": "MutationGameProcessTapsBatch",
            "variables": {
                "payload": {
                    "nonce": "cb467f0785fa0e8e62a55c1614b7d1c8084036d74f014422bfe799b8ead7ae67",
                    "tapsCount": 20
                }
            },
            "query": """
                mutation MutationGameProcessTapsBatch($payload: TelegramGameTapsBatchInput!) {
                    telegramGameProcessTapsBatch(payload: $payload) {
                        ...FragmentBossFightConfig
                        __typename
                    }
                }
                fragment FragmentBossFightConfig on TelegramGameConfigOutput {
                    _id
                    coinsAmount
                    currentEnergy
                    maxEnergy
                    weaponLevel
                    energyLimitLevel
                    energyRechargeLevel
                    tapBotLevel
                    currentBoss {
                        _id
                        level
                        currentHealth
                        maxHealth
                        __typename
                    }
                    freeBoosts {
                        _id
                        currentTurboAmount
                        maxTurboAmount
                        turboLastActivatedAt
                        turboAmountLastRechargeDate
                        currentRefillEnergyAmount
                        maxRefillEnergyAmount
                        refillEnergyLastActivatedAt
                        refillEnergyAmountLastRechargeDate
                        __typename
                    }
                    bonusLeaderDamageEndAt
                    bonusLeaderDamageStartAt
                    bonusLeaderDamageMultiplier
                    nonce
                    __typename
                }
            """
        }


    def login(self):
        if "Authorization" in self.headers:
            self.headers.pop("Authorization")
        user_obj = self.init_data["user"]
        tg_web_data = unquote(unquote(self.init_data_raw))
        user_data = tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0]
        data = {
            "operationName": "MutationTelegramUserLogin",
            "variables": {
                "webAppData": {
                    "auth_date": int(self.init_data["auth_date"]),
                    "hash": self.init_data["hash"],
                    "query_id": self.init_data["query_id"],
                    "checkDataString": f"auth_date={self.init_data['auth_date']}\nquery_id={self.init_data['query_id']}\nuser={user_data}",
                    "user": {
                        "id": user_obj["id"],
                        "allows_write_to_pm": user_obj["allows_write_to_pm"],
                        "first_name": user_obj["first_name"],
                        "last_name": user_obj["last_name"],
                        "username": user_obj.get("username", "Username không được đặt"),
                        "language_code": user_obj["language_code"],
                        "version": "7.2",
                        "platform": "ios"
                    }
                }
            },
            "query": QUERY_LOGIN
        }
        # print(data)
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy, json=data)
            # res = self.browser_post(url, data)
            data = res.json()
            self.access_token = data["data"]["telegramUserLogin"]["access_token"]
            self.update_header("Authorization", f"Bearer {self.access_token}")
            return True
        except Exception as e:
            self.bprint(f"Errorr: {res.status_code}")
            return False

    def get_user_info(self):
        if self.access_token is None:
            self.login()
            if self.access_token is None:
                self.bprint("Login not work, stop processing")
                return None

        body = {
            "operationName": "QUERY_GAME_CONFIG",
            "variables": {},
            "query": QUERY_GAME_CONFIG
        }
        try:
            res = requests.post(url, headers=self.headers, proxies=self.proxy, json=body)
            data = res.json()
            self.remain_boost = int(data['data']['telegramGameGetConfig']['freeBoosts']['currentRefillEnergyAmount'])
            return data['data']['telegramGameGetConfig']
        except Exception as e:
            self.bprint("Failed to get user info")
            return None


    def get_nonce(self, length = 52):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def recharge_energy(self):
        if self.access_token:
            if self.remain_boost > 0:
                boostpayload = {
                    "operationName": "telegramGameActivateBooster",
                    "variables": {
                        "boosterType": "Recharge"
                    },
                    "query": """mutation telegramGameActivateBooster($boosterType: BoosterType!) {
                        telegramGameActivateBooster(boosterType: $boosterType) {
                            ...FragmentBossFightConfig
                            __typename
                        }
                    }

                    fragment FragmentBossFightConfig on TelegramGameConfigOutput {
                        _id
                        coinsAmount
                        currentEnergy
                        maxEnergy
                        weaponLevel
                        energyLimitLevel
                        energyRechargeLevel
                        tapBotLevel
                        currentBoss {
                            _id
                            level
                            currentHealth
                            maxHealth
                            __typename
                        }
                        freeBoosts {
                            _id
                            currentTurboAmount
                            maxTurboAmount
                            turboLastActivatedAt
                            turboAmountLastRechargeDate
                            currentRefillEnergyAmount
                            maxRefillEnergyAmount
                            refillEnergyLastActivatedAt
                            refillEnergyAmountLastRechargeDate
                            __typename
                        }
                        bonusLeaderDamageEndAt
                        bonusLeaderDamageStartAt
                        bonusLeaderDamageMultiplier
                        nonce
                        __typename
                    }"""
                }
                try:
                    res = requests.post(url, headers=self.headers, json= boostpayload, proxies=self.proxy)
                    data = res.json()
                    if "errors" in data:
                        self.bprint("Recharged failed")
                        return False
                    return True
                except Exception as e:
                    return False

    def claim(self):
        userinfo = self.get_user_info()
        print(userinfo)
        if userinfo is None:
            self.bprint("Get user info failed, May be you need to check")
            self.wait_time = 60*60 # Wait 1 hrs
        else:
            
            curenegy = int(userinfo['currentEnergy'])
            coinamount = userinfo['coinsAmount']
            while curenegy > 200:
                self.bprint(f"Balance 💎 : {coinamount}")
                self.bprint(f"Remain energy: {curenegy} / {userinfo['maxEnergy']}")
                self.claimbody["variables"]["payload"]["tapsCount"] = random.randint(10, 100)
                self.claimbody["variables"]["payload"]["nonce"] = self.get_nonce()
                try:
                    response = requests.post(url, headers=self.headers, json=self.claimbody, proxies=self.proxy)
                    data = response.json()
                    userinfo = self.get_user_info()
                    coinamount = data['data']['telegramGameProcessTapsBatch']['coinsAmount']
                    curenegy = data['data']['telegramGameProcessTapsBatch']['currentEnergy']
                except Exception as e:
                    self.bprint(e)
                time.sleep(1)
            self.bprint("Enerny is low. Try recharging...")
            if self.recharge_energy():
                self.bprint("Recharge success, call claim again")
                return self.claim()
            else:
                self.bprint("Recharge failed, maybe not enough free boost")
            self.bprint("Wait 30 mins for next iteration")
            self.wait_time = 30*60

    def parse_config(self, cline):
        self.parse_init_data_raw(cline["init_data"])

    # def browser_post(self, url, data):
    #     async def post_async():
    #         async with aiohttp.ClientSession() as session:
    #             async with session.post(url, headers=self.headers, json = data) as response:
    #                 # print(response.status_code)
    #                 return await response.json()

    #     loop = asyncio.get_event_loop()
    #     return loop.run_until_complete(post_async())

if __name__ == "__main__":
    cline = {
		"coin": "memefi",
		"init_data": "query_id=AAGSXjtPAgAAAJJeO08n-Ybf&user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22The%20Meoware%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22themeoware%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1717825475&hash=7b082226ad67778b6a3a068f64010add096f7f2a2c6021f862847bf6e95281f4",
		"type": "socks5"
	}
    obj = memefi()
    obj.parse_config(cline)
    obj.login()
    obj.remain_boost = 1
    obj.claim()
    # obj.claim() 
    # obj.get_nonce()