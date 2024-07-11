import threading
import time
import json
import modules
from utils import *
import urllib.parse
import sys
import queue
from proxyhelper import ProxyHelper, ProxyMode, ReturnCode, Proxy
from globalconfig import *
from utils import get_random_ua

class workerhelper:
	proxy = None
	last_request = 0
	def __init__(self):
		pass

	@staticmethod
	def gen_proxy():
		if GLOBAL_PROXY_MODE == ProxyMode.PROXY_DIRECT:
			return None
		obj = ProxyHelper("proxy.txt", GLOBAL_PROXY_MODE, GLOBAL_PROXY_TYPE, GLOBAL_PROXY_USER_PASS_MODE)
		cur = time.time()
		if cur > (workerhelper.last_request + GLOBAL_PROXY_GET_DELAY):
			ret, p = obj.get_proxy()
			if ret == True:
				workerhelper.last_request = cur
				workerhelper.proxy = p
				return workerhelper.proxy
			else:
				print(f"Failed to get proxy {p.value}")
				return None
		else:
			return workerhelper.proxy
		
	@staticmethod
	def build_proxy(proxy, type):
		type = ProxyType(type.lower())
		return Proxy(proxystr=proxy, proxytype=type).build()

class worker(threading.Thread):
	# inqueue: give me a queue, I will get the config line
	def __init__(self, inqueue, registercb, request_locking = None, print_locking = None):
		threading.Thread.__init__(self)
		self.q = inqueue
		self.cb = registercb
		if self.validate_cb() == False:
			print("The callback much be a function with 2 arguments")
			sys.exit(1)
		self.running = True
		self.coin = None
		self.print_lock = print_locking
		self.lock_request = request_locking
	
	def stop(self):
		self.running = False
		
	def validate_cb(self):
		if not callable(self.cb):
			return False

		# Check if the object is a function or a method with two parameters
		sig = inspect.signature(self.cb)
		return len(sig.parameters) == 2

	def validate_cline(self, cline):
		try:
			self.coin = cline['coin']
			self.params = cline
			return True
		except Exception as e:
			return False
	 
	def acquire_lock(self):
		if self.lock_request:
			self.lock_request.acquire()
		
	def release_lock(self):
		if self.lock_request and self.lock_request.locked():
			self.lock_request.release()

	def run(self):
		while self.running:
			try:
				cline = self.q.get_nowait()
			except queue.Empty:
				time.sleep(1)
				continue
			try:
				if self.validate_cline(cline):
					ins = create_instances(import_one_module(modules, self.coin))
					print(f"Creating instance for {self.coin}")
					if "Proxy" in cline:
						proxy = workerhelper.build_proxy(cline["Proxy"], cline["type"])
					else:
						proxy = workerhelper.gen_proxy()
					ins.set_proxy(proxy)
					if "ua" not in cline:
						ins.set_ua(get_random_ua())
					else:
						ins.set_ua(cline["ua"])
					ins.parse_config(self.params)
					self.acquire_lock()
					ins.claim()
					if self.cb:
						print(f"Waiting {ins.wait_time} seconds for next run")
						self.cb(ins.wait_time, self.params)
					self.release_lock()
			except Exception as e:
				ins.bprint(e)
				print("Exception happen, please check the code")
				self.release_lock()
			finally:
				self.release_lock()
			self.q.task_done()

			

	
