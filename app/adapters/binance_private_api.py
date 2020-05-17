##########################################################################

# BINANCE API Connection
# Documentation ref can be found at: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md

##########################################################################

import time, json, hmac, hashlib, requests, os, sys
from urllib.parse import urljoin, urlencode
from sqlalchemy import create_engine, Table, MetaData, text, select
import pandas as pd
import numpy as np

from utilities import obtain_env_variable

API_KEY = obtain_env_variable('BINANCE_API_KEY', 'BINANCE_API_KEY')
SECRET_KEY = obtain_env_variable('BINANCE_API_SECRET', 'BINANCE_API_SECRET')
BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}

class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"

        # Python 2.x
        # super(BinanceException, self).__init__(message)
        super().__init__(message)




