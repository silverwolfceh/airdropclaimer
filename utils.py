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

def open_helper():
	url = 'https://anbusystem.github.io/autoairdrop/helper/confighelper.html'
	webbrowser.open_new_tab(url)

def check_update_data(corever: str, modver: str):
	url = "https://raw.githubusercontent.com/anbusystem/AutoAirdropClaimer/main/version.json"
	update_data = {
		"core" : {
			"update" : False,
			"url" : ""
		},
		"mod" : {
			"update" : False,
			"url" : ""
		}
	}
	try:
		res = requests.get(url)
		data = res.json()
		if corever != data["corever"]:
			update_data["core"]["update"] = True
			update_data["core"]["url"] = data["coreurl"]
		if modver != data["modver"]:
			update_data["mod"]["update"] = True
			update_data["mod"]["url"] = data["modurl"]
		return update_data
	except Exception as e:
		print("Check update failed")
		return None
	
def check_update(corever: str, modver: str):
	update_data = check_update_data(corever, modver)
	if update_data and update_data["core"]["update"]:
		execute_update("core", update_data["core"]["url"])
	
	if update_data and update_data["mod"]["update"]:
		execute_update("mod", update_data["mod"]["url"])

def execute_update(type, url):
	webbrowser.open_new_tab(url)