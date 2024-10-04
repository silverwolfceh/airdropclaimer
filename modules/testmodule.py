import requests
import time
import random
from urllib.parse import unquote
if __name__ == "__main__":
    from base import basetap
else:
    from .base import basetap

class testmodule(basetap):
    def __init__(self, proxy = None, headers = {}):
        super().__init__()
        self.token = None
        self.proxy = proxy
        self.headers = headers
        self.stopped = False
        self.name = self.__class__.__name__
        self.users = None

    def parse_config(self, cline):
        self.parse_init_data_raw(cline["init_data"])

    def get_all_user(self):
        url = 'https://dummyjson.com/users'
        data = self.get_data(url, None, fjson=True)
        self.users = data["users"]
    
    def login(self, user):
        url = 'https://dummyjson.com/user/login'
        body = {
            "username" : user["username"],
            "password" : user["password"],   
        }
        resdata = self.post_data(url, body)
        if resdata and "email" in resdata:
            self.bprint(f"Welcome {resdata['firstName']} {resdata['lastName']} to my house")

    def claim(self):
        if self.users is None:
            self.get_all_user()
        user = self.users[random.randint(0, len(self.users) - 1)]
        self.login(user)
