from django.test import TestCase

from models import PokerTable
from collections import deque
from collections import Counter
import re
import os
import asyncio

from aptos_sdk.account import Account
from aptos_sdk.async_client import ApiError, FaucetClient, ResourceNotFound, RestClient


async def main():
    NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
    FAUCET_URL = os.getenv(
        "APTOS_FAUCET_URL",
        "https://faucet.devnet.aptoslabs.com",
    )
    PokerTablePublicAddress = "0x31cd6604b0c53f8bf4b40b91b8bac45bddd183cb35ac6f4a4c6eaac398990399"
    PokerTablePrivateKey = "0x9515061f2c7a53c3c6a1b731adf54be869faee1a86fbd433d49687388cd3f9c1"
    # 得到 pokerTab 用于调用智能合约
    rest_client = RestClient(NODE_URL)  # 连接到devnet所用的一个fullNode
    faucet_client = FaucetClient(FAUCET_URL, rest_client)
    pokerTab = Account.load_key(PokerTablePrivateKey)
    payload = {
        "type": "entry_function_payload",
        "function": "code::publish_package_txn",
        "type_arguments": [],
        "arguments": [
            f"{PokerTablePublicAddress}",
        ],
    }
    getFirstHandTxHash = await rest_client.submit_transaction(pokerTab, payload)
    FirstHandRes = await rest_client.transaction_by_hash(getFirstHandTxHash)
    print(FirstHandRes)


asyncio.run(main())
# Create your tests here.
