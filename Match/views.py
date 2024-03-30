from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from .services import add_player_to_queue
from .services import active_games
from .services import checkValid
from .services import checkOverField
from .services import dealRank
from .models import PokerTable

from typing import Optional


def join_game_queue(request):
    wallet_address = request.GET.get('wallet_address')
    g_id = -1
    cards = []
    outCardRight = False
    if not wallet_address:
        return JsonResponse({'error': 'Wallet address is required.'}, status=400)
    add_player_to_queue(wallet_address)
    # 交给 守护线程处理 匹配
    return JsonResponse({'message': 'joined, in matching'})


'''        
        # 仅当得到res 为 True 时跳出循环

        res, game_id, playerCards, outRight = check_and_start_game(wallet_address)
        if res:
            g_id = game_id
            cards = playerCards
            outCardRight = outRight
            break
    jsonCards = JsonResponse(cards)
    return JsonResponse(
        {'Matching Status': "Started", 'gameId': str(g_id), 'Cards': jsonCards, 'outCardPower': str(outCardRight)})'''


def query_outcard_right(request):
    wallet_address = request.GET.get('wallet_address')
    game_id = request.GET.get('g_id')
    if not wallet_address or not game_id:
        return JsonResponse({'error': 'Missing wallet address or game ID'}, status=400)
    # 将字符串的 game_id 转换为整数，假设 game_id 存储时是整数形式
    try:
        game_id = int(game_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid game ID'}, status=400)
    pokerTable: Optional[PokerTable] = active_games.get(game_id).copy()
    if not pokerTable:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if pokerTable.currentHand == wallet_address:
        return JsonResponse({'message': 'Owned Rights'})
    else:
        return JsonResponse({'message': 'Not Owned Rights'})


def out_card(request):
    wallet_address = request.GET.get('wallet_address')
    game_id = request.GET.get('g_id')
    outedCards = request.GET.get('outedCards')
    # TODO: 与前端的接口处理 outedCards 传进来应该是一个字符串将outedCards 转为一个字符串列表
    if outedCards == "":
        return JsonResponse({'message': 'Pass Succeed'})
    if not wallet_address or not game_id:
        return JsonResponse({'error': 'Missing wallet address or game ID'}, status=400)
    # 将字符串的 game_id 转换为整数，假设 game_id 存储时是整数形式
    try:
        game_id = int(game_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid game ID'}, status=400)
    # TODO：可能会出问题,根据game_id从字典active_games中获得前端玩家对应的PokerTable,使用浅拷贝
    pokerTable: Optional[PokerTable] = active_games.get(game_id).copy()
    if not pokerTable:
        return JsonResponse({'error': 'Game not found'}, status=404)

    # 返回值，默认为一些空值，前端据此进行判定
    getPos = -1
    getSingleWin = ""
    getAllWin = ""
    # 牌型合法 and 大于桌面牌
    if checkValid(outedCards, pokerTable.currentGrade) and (len(pokerTable.FieldCard) == 0) or checkOverField(
            outedCards, pokerTable.FieldCard, pokerTable.currentGrade):
        # 减少玩家手牌
        for card in outedCards:
            # 这里card命名格式如 diamonds 7 ，故不会误删
            pokerTable.playerCards[wallet_address].remove(card)
        # 修改桌面牌
        pokerTable.FieldCard = outedCards
        print("玩家出牌大于桌面牌，出牌成功！")
        # 判断当前出牌玩家是否打完手牌
        if len(pokerTable.playerCards[wallet_address]) == 0:
            # 打完手牌，处理胜利逻辑: 当前玩家得到第几游，当前玩家所属队伍是否获得本副牌胜利，当前玩家是否获得最终胜利
            getPos, getSingleWin, getAllWin = dealRank(pokerTable, wallet_address)
            return JsonResponse({'message': 'Card played successfully and get Pos',
                                 'getPos': getPos, 'getSingleWin': getSingleWin, 'getAllWin': getAllWin})
        else:
            # TODO: 通知下一个玩家出牌 , 如何通知？！！！！！ 找找方法
            # 未打完手牌
            return JsonResponse({'message': 'Card played successfully but not no Pos',
                                 'getPos': getPos, 'getSingleWin': getSingleWin, 'getAllWin': getAllWin})
        # 不论是否打开手牌都会返回 success 的message

    # 下面两种情况属于打不出牌，前端收到相应response后根据 message 字段得知结果做出对应处理
    # 牌型不合法
    elif not checkValid(outedCards, pokerTable.currentGrade):
        return JsonResponse({'message': 'Card Played invalid',
                             'getPos': getPos, 'getSingleWin': getSingleWin, 'getAllWin': getAllWin})
    # 小于桌面牌
    else:
        return JsonResponse({'message': 'Card Played small than fieldCards',
                             'getPos': getPos, 'getSingleWin': getSingleWin, 'getAllWin': getAllWin})
