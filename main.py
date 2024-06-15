import queue
import time
import threading
import signal
import json
import sys
from utils import open_helper, check_update
from worker import worker
from modules.base import MODULE_VER

APP_VERSION = "2.2"

worker_queue = queue.Queue()
is_app_running = True
worker_queue_lock = threading.Lock()
threads = []
max_threads = 5
# request_locking = threading.Lock()
request_locking = None

def signal_handler(sig, frame):
    global is_app_running
    is_app_running = False

def thread_wait_and_pushback(wait_time, cline):
    global is_app_running, worker_queue, worker_queue_lock
    sleeped_time = 0
    while is_app_running and sleeped_time < wait_time:
        time.sleep(1)
        sleeped_time = sleeped_time + 1
    with worker_queue_lock:
        worker_queue.put(cline)
    return

def schedule_new_iteration(wait_time, cline):
    t = threading.Thread(target=thread_wait_and_pushback, args=(wait_time, cline))
    t.start()

def load_config(configfile = "config.json"):
    with open(configfile) as f:
        data = f.read()
        try:
            config = json.loads(data)
            return config
        except Exception as e:
            print(f"The {configfile} is wrong")
    return None

def is_config_valid(c):
    if "coin" in c:
        return True
    return False

def initialized_app(configfile):
    global threads, worker_queue, request_locking, max_threads
    config = load_config(configfile)
    if config == None:
        print("Exit")
        sys.exit(1)

    valid = False
    for c in config:
        if is_config_valid(c):
            worker_queue.put(c)
            valid = True

    if not valid:
        print(f"The {configfile} is not valid, ensure to generate it using confighelper")
        open_helper()
        sys.exit(1)
    
    print(f"Start launching {max_threads} threads...")
    for i in range(0, max_threads):
        t = worker(worker_queue, schedule_new_iteration, request_locking)
        threads.append(t)

intro = '''
    _         _             _    _         _                    ____ _       _                     
   / \  _   _| |_ ___      / \  (_)_ __ __| |_ __ ___  _ __    / ___| | __ _(_)_ __ ___   ___ _ __ 
  / _ \| | | | __/ _ \    / _ \ | | '__/ _` | '__/ _ \| '_ \  | |   | |/ _` | | '_ ` _ \ / _ \ '__|
 / ___ \ |_| | || (_) |  / ___ \| | | | (_| | | | (_) | |_) | | |___| | (_| | | | | | | |  __/ |   
/_/   \_\__,_|\__\___/  /_/   \_\_|_|  \__,_|_|  \___/| .__/   \____|_|\__,_|_|_| |_| |_|\___|_|   
                                                      |_|                                          
'''
if __name__ == "__main__":
    check_update(APP_VERSION, MODULE_VER)
    print(intro)
    print(f"Build information | App: {APP_VERSION}, Script: {MODULE_VER}")
    signal.signal(signal.SIGINT, signal_handler)
    configfile = "config.json"
    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    elif len(sys.argv) == 3:
        configfile = sys.argv[2]
        max_threads = int(sys.argv[1])
    initialized_app(configfile)
    for t in threads:
        t.start()
        time.sleep(1)
    while is_app_running:
        time.sleep(1)
    
    for t in threads:
        t.stop()
        # t.join()