import time
import json
import requests
import urllib.parse

TIME_WAIT = 10
MODULE_VER = "2.2"
def print_green_line(line):
    GREEN = "\033[92m"
    RESET = "\033[0m"
    print(f"{GREEN}{line}{RESET}")

class basetap:
    def __init__(self):
        self.stopped = False
        self.wait_time = TIME_WAIT
        self.name = self.__class__.__name__
        self.oldbalance = 0
        self.headers = {}
        self.init_data = {}
        self.init_data_raw = ""
        self.init_data_load = False
        self.modver = "v1.0"
        self.printlock = False

    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        pass

    def set_print_lock(self, lock):
        self.printlock = lock

    def acquire_lock(self):
        if self.printlock:
            self.printlock.acquire()
        
    def release_lock(self):
        if self.printlock and self.printlock.locked():
            self.printlock.release()

    def set_ua(self, ua):
        uastr = ua
        if isinstance(ua, str):
            pass
        else:
            uastr = ua()
        self.update_header("User-Agent", uastr)
        self.update_header("user-agent", uastr)
            
    def parse_config(self, cline):
        self.bprint("You should implement the parse config function")

    def parse_init_data(self, initdata):
        initstr = ""
        data = initdata.split("&")
        for d in data:
            k,v = d.split("=")
            self.init_data[k] = v
            initstr += k + "=" + urllib.parse.quote(v, safe='') + "&"
        self.init_data_raw = initstr
        self.init_data_load = True
    
    def parse_init_data_raw(self, rawdata):
        data = rawdata.split("&")
        for d in data:
            try:
                k,v = d.split("=")
                if k == "user":
                    v = json.loads(urllib.parse.unquote(v))
                self.init_data[k] = v
            except Exception as e:
                pass
        self.init_data_raw = rawdata
        self.init_data_load = True

    def is_init_data_ready(self):
        return self.init_data_load

    def update_header(self, k, v):
        self.headers[k] = v

    def set_proxy(self, proxy):
        self.proxy = proxy

    def stop(self):
        self.stopped = True
        self.acquire_lock()
        print(f"{self.name}: stopped" )
        self.release_lock()

    def set_name(self, myname):
        self.name = myname

    def print_balance(self, bl):
        accname = self.init_data["user"]["first_name"] if self.init_data_load else ""
        if int(bl) > self.oldbalance:
            self.acquire_lock()
            print_green_line(f"{self.name}-{accname}: Balance 💎: {bl:,.0f} ^")
            self.release_lock()
            self.oldbalance = int(bl)
        else:
            self.acquire_lock()
            print(f"{self.name}-{accname}: Balance 💎: {bl:,.0f}")
            self.release_lock()

    def bprint(self, msg):
        accname = self.init_data["user"]["username"] if self.init_data_load else ""
        self.acquire_lock()
        print(f"{self.name}-{accname}: {msg}")
        self.release_lock()

    def cprint(self, msg):
        accname = self.init_data["user"]["username"] if self.init_data_load else ""
        print_green_line(f"{self.name}-{accname}: {msg}")

    def wait(self):
        print(f"{self.name}: wait {self.wait_time}s" )
        sleeped = 0
        while sleeped < self.wait_time and self.stopped == False:
            time.sleep(1)
            sleeped = sleeped + 1
    
    def claim(self):
        self.bprint("You should implement this function")

    def request_data_json(self, type, url, data):
        try:
            if type == "post":
               res = requests.post(url, json=data, headers=self.headers, proxies=self.proxy)
               res.raise_for_status()
               return res
            elif type == "get":
               res = requests.get(url, json=data, headers=self.headers, proxies=self.proxy)
               res.raise_for_status()
               return res
        except Exception as e:
            self.bprint(e)
        return None
    
    def get_data(self, url, data, fjson = True):
        data = self.request_data_json("get", url, data)
        if data != None and fjson:
            return data.json()
        elif data != None:
            return data
        return None
    
    def post_data(self, url, data, fjson = True):
        data = self.request_data_json("post", url, data)
        if data != None and fjson:
            return data.json()
        elif data != None:
            return data
        return None
    
if __name__ == "__main__":
    obj = basetap()
    data_raw = "query_id=AAGSXjtPAgAAAJJeO0_2-sHt&user=%7B%22id%22%3A5624258194%2C%22first_name%22%3A%22Evis%22%2C%22last_name%22%3A%22The%20Cat%22%2C%22username%22%3A%22rokbotsxyz%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1716722443&hash=40fe84e8f626ff0fa74c3f0e7c51c677fac5da8b27a0fc8ddd0fb5cdc5ace2a3"
    data = data_raw.split("&")
    init_data = {}
    for d in data:
        k,v = d.split("=")
        
        if k == "user":
            v = json.loads(urllib.parse.unquote(v))
        
        init_data[k] = v
    print(init_data["user"]["id"])
