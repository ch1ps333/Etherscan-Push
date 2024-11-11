import redis
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
import requests
import database
from message_handler import send_notification
from random import randint

load_dotenv()

API_KEY = getenv('ETHERSCAN_API')

def get_eth_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    
    if 'ethereum' in data:
        return data['ethereum']['usd']
    else:
        return None

def get_transactions(address, api_key, start_block=0, end_block=99999999):
    url = f'https://api.etherscan.io/api'
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': start_block,
        'endblock': end_block,
        'sort': 'desc', 
        'apikey': api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == '1':
        return data['result']
    else:
        return None

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def process_transaction(config, group, tx, eth_price, tx_time):
    tx_hash = tx['hash']
    
    group_tx_key = f"group:{group.tg_id}:tx:{tx_hash}"

    if redis_client.exists(group_tx_key):
        return 

    tx_link = f"https://etherscan.io/tx/{tx_hash}"
    value_in_eth = round(int(tx['value']) / 10**18, 2)
    value_in_usd = round(value_in_eth * eth_price, 1)
    gas_price_in_eth = int(tx['gasPrice']) / 10**18
    gas_in_usd = round(gas_price_in_eth * eth_price * int(tx['gas']), 1)
    timestamp = int(tx['timeStamp'])
    tx_time = datetime.utcfromtimestamp(timestamp)
    gas = int(tx['gasPrice'])
    trans_gas = gas / 10**9
    trans_gas = f"{trans_gas:.9f}"
    
    res = await database.add_group_transaction_sum(group.tg_id, int(value_in_usd))
    transactionSum = await database.get_group_trans_sum(group.tg_id)
    await send_notification(config.template_message, group.tg_id, tx_hash, tx_link, tx['blockNumber'], tx['from'], tx['to'], value_in_usd, value_in_eth, gas_in_usd, trans_gas, transactionSum, tx_time.strftime('%Y-%m-%d %H:%M:%S'))

    redis_client.setex(group_tx_key, timedelta(hours=2), 1)

async def collect_transactions():
    while True:
        try:
            config = await database.get_config()
            groups = await database.get_all_groups()

            eth_price = None
            while eth_price is None:
                eth_price = get_eth_price()
                if eth_price is None:
                    await asyncio.sleep(10) 

            if groups:
                for group in groups:
                    if group.status:

                        addresses = await database.get_addresses(group.tg_id)

                        for address in addresses:

                            transactions = get_transactions(address, API_KEY)

                            if transactions:

                                for tx in transactions[:20]:
                                    value_in_eth = int(tx['value']) / 10**18
                                    value_in_usd = value_in_eth * eth_price

                                    if value_in_usd >= group.min_amount and value_in_usd <= group.max_amount:
                                        tx_hash = tx['hash']
                                        tx_link = f"https://etherscan.io/tx/{tx_hash}"
                                        gas_price_in_eth = int(tx['gasPrice']) / 10**18
                                        gas_in_usd = gas_price_in_eth * eth_price * int(tx['gas'])
                                        timestamp = int(tx['timeStamp'])

                                        tx_time = datetime.utcfromtimestamp(timestamp)

                                        current_time = datetime.utcnow()
                                        time_diff = current_time - tx_time

                                        address_info = await database.get_address(address, group.tg_id)

                                        if time_diff <= timedelta(hours=1) and ((tx['from'] == address and address_info.transactions_from == True) or (tx['to'] == address and address_info.transactions_to == True)):
                                            await process_transaction(config, group, tx, eth_price, tx_time)
                                            await asyncio.sleep(1)
                                            break
            await asyncio.sleep(randint(config.info_collect_interval_from, config.info_collect_interval_to) * 60)

        except Exception as e:
            print(f"Ошибка: {e}")

    redis.close()
    await redis.wait_closed()



asyncio.run(collect_transactions())
