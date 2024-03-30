from queue import Queue
import threading
import time
from collections import deque
import os
import asyncio
from .models import PokerTable

from aptos_sdk.account import Account
from aptos_sdk.async_client import ApiError, FaucetClient, ResourceNotFound, RestClient
from aptos_sdk.authenticator import Authenticator, FeePayerAuthenticator
from aptos_sdk.bcs import Serializer
from aptos_sdk.transactions import (
    EntryFunction,
    FeePayerRawTransaction,
    SignedTransaction,
    TransactionArgument,
    TransactionPayload,
)

# 存储正在进行的游戏实例
active_games = {}
# 记录当前已经产生的对局数量
games_id = 0
waiting_queue = deque()
queue_lock = threading.Lock()  # 创建互斥锁

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


def match_making():
    global games_id
    global waiting_queue
    global active_games
    while True:
        # 模拟匹配逻辑
        if len(waiting_queue) >= 4:
            # 创建游戏对象实例
            games_id += 1
            active_games[games_id] = createPokerTable()
            print(f"匹配到玩家:")
            poT = active_games[games_id]
            for i in range(4):
                print(poT.players[i])
        time.sleep(1)  # 用于模拟匹配检查间隔


async def createPokerTable():
    global waiting_queue
    global pokerTab

    poker_table = PokerTable()
    poker_table.game_id = games_id

    with queue_lock:
        poker_table.players[0] = waiting_queue.popleft()
        poker_table.players[1] = waiting_queue.popleft()
        poker_table.players[2] = waiting_queue.popleft()
        poker_table.players[3] = waiting_queue.popleft()

    # 这里可以实现游戏开始的逻辑
    payload = {
        "type": "entry_function_payload",
        "function": "0x1::GuanDan::team",
        "type_arguments": [],
        "arguments": [
            f"{PokerTablePublicAddress}",
            poker_table.players,
        ],
    }

    getTeamTxHash = await rest_client.submit_transaction(pokerTab, payload)
    TeamRes = await rest_client.transaction_by_hash(getTeamTxHash)
    # TODO: 根据TeamRes分配队伍
    poker_table.teamAPlayers.append(poker_table.players[0])
    poker_table.teamAPlayers.append(poker_table.players[1])
    poker_table.teamBPlayers.append(poker_table.players[2])
    poker_table.teamBPlayers.append(poker_table.players[3])

    payload = {
        "type": "entry_function_payload",
        "function": "0x2::GuanDan::cards",
        "type_arguments": [],
        "arguments": [
            f"{PokerTablePublicAddress}",
        ],
    }
    getCardsTxHash = await rest_client.submit_transaction(pokerTab, payload)
    CardsRes = await rest_client.transaction_by_hash(getCardsTxHash)
    # TODO: 根据CardsRes分配队伍
    poker_table.playerCards[poker_table.players[0]] = ""
    poker_table.playerCards[poker_table.players[1]] = ""
    poker_table.playerCards[poker_table.players[2]] = ""
    poker_table.playerCards[poker_table.players[3]] = ""

    payload = {
        "type": "entry_function_payload",
        "function": "0x3::GuanDan::FirstHand",
        "type_arguments": [],
        "arguments": [
            f"{PokerTablePublicAddress}",
        ],
    }
    getFirstHandTxHash = await rest_client.submit_transaction(pokerTab, payload)
    FirstHandRes = await rest_client.transaction_by_hash(getFirstHandTxHash)
    # TODO: 根据CardsRes分配队伍
    poker_table.currentHand = poker_table.players[FirstHandRes]

    return poker_table

