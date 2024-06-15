from enum import Enum
import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxyMode(Enum):
    PROXY_ROTATION = 0
    PROXY_LIST = 1
    PROXY_FLEX = 2
    PROXY_DIRECT = 3

class ProxyType(Enum):
    SOCKS5 = "socks5"
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"

class ReturnCode(Enum):
    OK = "LOCAL"
    FMT = "Format wrong"
    DIE = "Proxy is dead"
    EMPT = "No more proxy"

class ProxyAuthUserPass(Enum):
    FIRST = 0
    LAST = 1

NORMAL_PROXY = 2 # Type, host, port
AUTH_PROXY = 4 # Type : host : port : user : pass

class Proxy:
    def __init__(self, proxystr, userpassmode = ProxyAuthUserPass.LAST, proxytype = ProxyType.SOCKS5):
        self.data = proxystr.split(":")
        self.valid = True
        self.proxytype = proxytype.value
        self.userpassmode = userpassmode
        self.type = NORMAL_PROXY
        if len(self.data) == NORMAL_PROXY or len(self.data) == AUTH_PROXY:
            self.valid = True
            self.type = len(self.data)
        else:
            self.valid = False

    def build(self):
        if not self.valid:
            return None
        if self.type == NORMAL_PROXY:
            url = f"{self.proxytype}://{self.data[0]}:{self.data[1]}"
        elif self.userpassmode == ProxyAuthUserPass.LAST:
            url = f"{self.proxytype}://{self.data[2]}:{self.data[3]}@{self.data[0]}:{self.data[1]}"
        else:
            url = f"{self.proxytype}://{self.data[0]}:{self.data[1]}@{self.data[2]}:{self.data[3]}"
        proxy = {
            "http" : url,
            "https" : url
        }
        return proxy

class ProxyHelper:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProxyHelper, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, proxyfile = "proxy.txt", proxymode = ProxyMode.PROXY_ROTATION, proxytype = ProxyType.SOCKS5, mode = ProxyAuthUserPass.FIRST):
        self.proxyfile = proxyfile
        self.proxymode = proxymode
        self.proxytype = proxytype
        self.userpassmode = mode
        self.proxies = []
        self.rotationkey = ""
        self.died = 0
        self.currentidx = 0
        if self._is_proxy_mode_valid(proxymode):
            with open(self.proxyfile) as f:
                if self._is_proxy_mode(ProxyMode.PROXY_ROTATION):
                    self.rotationkey = f.readline().replace("\r", "").replace("\n", "")
                elif self._is_proxy_mode(ProxyMode.PROXY_LIST):
                    lines = f.readlines()
                    self.proxies = [line.replace('\r', '').replace('\n', '') for line in lines]
                else:
                    # Todo: implement more proxy mode here
                    pass
    
    # Check if we support proxy mode or not
    def _is_proxy_mode_valid(self, mode):
        if mode == ProxyMode.PROXY_ROTATION or mode == ProxyMode.PROXY_LIST or mode == ProxyMode.PROXY_DIRECT:
            return True
        return False

    # Check if the input is already a built proxy
    def _is_built(self, proxy):
        if isinstance(proxy, (dict, list)):
            return True
        return False

    # Build proxy object from string
    def _build_proxy(self, proxy : str):
        return Proxy(proxy, self.userpassmode, self.proxytype).build()
    
    # Implement the API to get rotation proxy from service
    def _get_rotation_proxy(self):
        url = f"https://apikey.site/key/get-new-ip?key={self.rotationkey}"
        try:
            res = requests.get(url, verify=False)
            data = res.json()
            # print(data)
            if "error" in data:
                print(data["message"])
                return None
            elif "data" in data and "host" not in data["data"]:
                print(data["message"])
                return None
            else:
                ipdata = data["data"]
                if self.proxytype == ProxyType.SOCKS5:
                    return "%s:%s:%s" % (ProxyType.SOCKS5.value, ipdata["host"], ipdata["socksPort"])
                return "http:%s:%s" % (ipdata["host"], ipdata["port"])
        except Exception as e:
            print(e)
            return None

    # Get the next proxy in file
    def _get_next_proxy(self, rotation):
        if self.currentidx >= len(self.proxies):
            if rotation:
                self.currentidx = 0
            else:
                return None
        p = self.proxies[self.currentidx]
        self.currentidx = self.currentidx + 1
        return p
    
    # Check if proxy is live or die
    def is_proxy_live(self, proxy):
        if not self._is_built(proxy):
            proxy = self._build_proxy(proxy)
        url = "https://ip-api.com/json/"
        try:
            res = requests.get(url, proxies=proxy)
            data = res.json()
            if "status" in data:
                return True
        except Exception as e:
            pass
        return False

    def _is_proxy_mode(self, proxymode : ProxyMode):
        return self.proxymode == proxymode

    def get_proxy(self, checklive = True, rotation = True):
        proxystr = ""
        if self._is_proxy_mode(ProxyMode.PROXY_ROTATION):
            proxystr = self._get_rotation_proxy()
        elif self._is_proxy_mode(ProxyMode.PROXY_LIST):
            proxystr = self._get_next_proxy(rotation)
        else:
            return True, None

        if proxystr == None:
            return False, None

        if checklive:
            if self.is_proxy_live(proxystr):
                pass
            else:
                if self._is_proxy_mode(ProxyMode.PROXY_LIST):
                    self.died = self.died + 1
                    print(f"{proxystr} dead")
                    if self.died >= len(self.proxies):
                        print("All proxy are dead.")
                        return False, ReturnCode.EMPT
                return self.get_proxy(checklive)
        proxy = self._build_proxy(proxystr)
        if proxy == None:
            return False, ReturnCode.FMT
        return True, proxy
    
    def is_valid_proxy(self, proxy):
        return self._is_built(proxy)

if __name__ == "__main__":
    obj = ProxyHelper(proxyfile="proxy.txt", proxymode=ProxyMode.PROXY_ROTATION)
    print(obj.get_proxy(True))