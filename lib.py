import requests
# import hashlib
# import hmac
# import json
from urllib.parse import urlencode
from enum import Enum
from time import time
import base64
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class Backpack:

    class KlineInterval(Enum):
        ONE_MINUTE = '1m'
        THREE_MINUTES = '3m'
        FIVE_MINUTES = '5m'
        FIFTEEN_MINUTES = '15m'
        THIRTY_MINUTES = '30m'
        ONE_HOUR = '1h'
        TWO_HOURS = '2h'
        FOUR_HOURS = '4h'
        SIX_HOURS = '6h'
        EIGHT_HOURS = '8h'
        TWELVE_HOURS = '12h'
        ONE_DAY = '1d'
        THREE_DAYS = '3d'
        ONE_WEEK = '1w'
        ONE_MONTH = '1month'


    def __init__(self, public_key: str, private_key: str):
        self.__public_key = public_key
        self.__private_key = private_key


    def __header(self):
        header = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive'
        }
        return header
    

    def __header_private(self, timestamp: int, signature: str, window: int = 5000):
        header = {
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'X-API-KEY': base64.b64encode(self.__public_key.encode()),
            'X-SIGNATURE': signature,
            'X-TIMESTAMP': timestamp,
            'X-WINDOW': window
        }
        return header


    def __get(self, request_path, params=''):
        base_url = 'https://api.backpack.exchange/'
        url = base_url + request_path + params
        header = self.__header()
        try:
            response = requests.get(url, headers=header)
            response.raise_for_status()
        except requests.exceptions.RequestException as errex:
            return errex
        return response.json()


    def __signature(self, timestamp: int, instruction: str, params: str = ''):
        # order params alphabetically
        if params != '':
            ordered_params = params.split('&').sort().join('&')
        else:
            ordered_params = ''
        completed_params = f'instruction={instruction}' + ordered_params + f'&timestamp={timestamp}&window=5000'
        loaded_private_key = load_pem_private_key(self.__private_key.encode())
        signature = base64.b64encode(loaded_private_key.sign(completed_params.encode()))
        return signature


    def __get_private(self, request_path: str, instruction: str, params: str=''):
        base_url = 'https://api.backpack.exchange/'
        url = base_url + request_path + params
        timestamp = int(time() * 1000)
        signature = self.__signature(timestamp, instruction, params)
        header = self.__header_private(timestamp, signature)
        try:
            response = requests.get(url, headers=header)
            response.raise_for_status()
        except requests.exceptions.RequestException as errex:
            return errex
        return response.json()


    def status(self):
        """
        Get the current status of the platform.
        Returns:
            The status of the platform.
        """
        return self.__get('api/v1/status')

    
    def ping(self):
        """
        Ping the platform to receive a pong
        Returns:
            A pong from the platform.
        """
        url = 'https://api.backpack.exchange/api/v1/ping'
        header = self.__header()
        try:
            response = requests.get(url, headers=header)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as errex:
            return errex
    

    def time(self):
        """
        Get the current time of the platform.
        Returns:
            The current time of the platform.
        """
        return self.__get('api/v1/time')
    

    def get_trades(self, symbol: str, limit: int = 100):
        """
        Get the trades for a specific symbol.
        Args:
            symbol (str): The symbol to retrieve trades for. (Required)
            limit (int): The maximum number of trades to retrieve. Default is 100; max is 1000. (Optional)
        Returns:
            The trades for the specified symbol.
        """
        return self.__get('api/v1/trades', f'?symbol={symbol}&limit={limit}')
    

    def get_historical_trades(self, symbol: str, limit: int = 100, offset: int = 0):
        """
        Get the historical trades for a specific symbol.
        Args:
            symbol (str): The symbol to retrieve historical trades for. (Required)
            limit (int): Limit the number of trades returned. Default 100, maximum 1000. (Optional)
            offset (int): The starting point for the historical trades. Default is 0. (Optional)
        Returns:
            The historical trades for the specified symbol.
        """
        return self.__get('api/v1/trades/history', f'?symbol={symbol}&limit={limit}&offset={offset}')


    def get_assets(self):
        """
        Get all the assets that are supported by the exchange.
        Returns:
            All the assets that are supported by the exchange.
        """
        return self.__get('api/v1/assets')
    

    def get_markets(self):
        """
        Get all the markets that are supported by the exchange.
        Returns:
            All the markets that are supported by the exchange.
        """
        return self.__get('api/v1/markets')


    def get_ticker(self, symbol: str):
        """
        Get the ticker for a specific symbol.
        Args:
            symbol (str): The symbol to retrieve the ticker for. (Required)
        Returns:
            The ticker for the specified symbol.
        """
        return self.__get('api/v1/ticker', f'?symbol={symbol}')


    def get_tickers(self):
        """
        Get summarised statistics for the last 24 hours for all market symbols..
        Returns:
            Summarised statistics for the last 24 hours for all market symbols..
        """
        return self.__get('api/v1/tickers')


    def get_depth(self, symbol: str):
        """
        Get the order book for a specific symbol.
        Args:
            symbol (str): The symbol to retrieve the order book for. (Required)
        Returns:
            The order book for the specified symbol.
        """
        return self.__get('api/v1/depth', f'?symbol={symbol}')
    

    def get_kline(self, symbol: str, interval: KlineInterval):
        """
        Get the kline for a specific symbol.
        Args:
            symbol (str): The symbol to retrieve the kline for. (Required)
            interval (str): The interval for the kline. (Required)
            limit (int): The maximum number of kline to retrieve. Default is 100; max is 1000. (Optional)
        Returns:
            The kline for the specified symbol.
        """
        return self.__get('api/v1/klines', f'?symbol={symbol}&interval={interval.value}')
    

    def get_balances(self):
        """
        Get the balances for the authenticated user.
        Returns:
            The balances for the authenticated user.
        """
        return self.__get_private('api/v1/capital', 'balanceQuery')