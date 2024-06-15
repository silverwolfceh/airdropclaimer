from proxyhelper import ProxyHelper, ProxyMode, ProxyType, ProxyAuthUserPass
import time

mode = ProxyMode.PROXY_LIST
type = ProxyType.SOCKS5
auth = ProxyAuthUserPass.LAST

obj = ProxyHelper("proxy.txt", mode, type, auth)
while True:
    ret, proxy = obj.get_proxy(False, False)
    # print(proxy)
    if proxy == None:
        break
    is_live = obj.is_proxy_live(proxy)
    if not is_live:
        print(f"Proxy {proxy} is dead")
    else:
        print(f"Proxy {proxy} is live")
print("Done, sleeping")
time.sleep(10)