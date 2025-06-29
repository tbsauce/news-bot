from dotenv import load_dotenv
from apit212 import *
import os

load_dotenv('.env')

username: str = os.getenv('USER')
password: str = os.getenv('PASS')

api = Apit212()

api.setup(username=username, password=password, mode="demo")

equity = Equity(cred=api)

print(equity.auth_validate())

print(equity.get_funds())
