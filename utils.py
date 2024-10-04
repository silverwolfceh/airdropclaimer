import requests
import random
import json
import importlib
import pkgutil
import webbrowser
import inspect


def create_instances(module):
	for name, obj in inspect.getmembers(module):
		if inspect.isclass(obj) and obj.__module__ == module.__name__:
				return obj()
	return None

def import_one_module(package, mname):
	package_name = package.__name__
	for _, module_name, _ in pkgutil.iter_modules(package.__path__):
		if module_name == mname:
			full_module_name = f"{package_name}.{module_name}"
			importedm = importlib.import_module(full_module_name)
			return importedm
	return None


def get_random_ua():
	ualist = []
	with open("ua.json") as f:
		content = f.read()
		ualist = json.loads(content)
	ua = random.choice(ualist)
	if ua:
		return ua["ua"]
	return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"


class CONSTANT:
	HELPER_URL = 'https://silverwolfceh.github.io/airdropclaimer/confighelper.html'
	VERSION_URL = 'https://raw.githubusercontent.com/silverwolfceh/airdropclaimer/main/version.json'
	CORE_UPDATE_PATH = "binurl"
	PLUG_UPDATE_PATH = "zipurl"
	CORE = "CORE"
	PLUGIN = "PLUGIN"
	VERSION = "version"

def open_helper():
	webbrowser.open_new_tab(CONSTANT.HELPER_URL)

def get_update_info(corever: str, modver: str):
	try:
		coreupdateurl = None
		pluginupdateurl = None
		res = requests.get(CONSTANT.VERSION_URL)
		data = res.json()
		if CONSTANT.CORE in data and CONSTANT.PLUGIN in data:
			if corever != data[CONSTANT.CORE][CONSTANT.VERSION]:
				coreupdateurl = data[CONSTANT.CORE][CONSTANT.CORE_UPDATE_PATH]
			if modver != data[CONSTANT.PLUGIN][CONSTANT.VERSION]:
				pluginupdateurl = data[CONSTANT.PLUGIN][CONSTANT.PLUG_UPDATE_PATH]
			return True, coreupdateurl, pluginupdateurl
		else:
			print("Failed to check update")
	except Exception as e:
		print(e)
	return False, None, None
	
def check_update(corever: str, modver: str):
	ret, curl, purl = get_update_info(corever, modver)
	if ret:
		if curl:
			execute_update(CONSTANT.CORE, curl)
		if purl:
			execute_update(CONSTANT.PLUGIN, purl)
		restart_app()
		

def execute_update(type, url):
	webbrowser.open_new_tab(url)

def restart_app():
	pass