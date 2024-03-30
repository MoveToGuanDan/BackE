from .models import PokerTable
from .MatchMaking import waiting_queue, queue_lock, active_games
from collections import Counter
import re


# 定义全局变量
# 假设我们有一个简单的队列来存储等待匹配的玩家钱包地址


# 中英文对照表
CardsType = {
    '单张': 'Single',
    '对子': 'Pair',
    '三同张': 'Trips',
    '三连对': 'ThreePair',
    '三带二': 'ThreeWithTwo',
    '二连三': 'TwoTrips',
    '顺子': 'Straight',
    '同花顺': 'StraightFlush',
    '炸弹': 'Bomb',
    '天王炸': 'MaxBomb',
    '未知牌型': 'Unknown'
}


def add_player_to_queue(wallet_address):
    with queue_lock:
        waiting_queue.append(wallet_address)
    return True


# 修改为 websocket 通信，不用了
'''async def check_and_start_game(wallet_address):
    # 创建PokerTable实例
    outCardRight = False
    if poker_table.currentHand == wallet_address:
        outCardRight = True
    # 返回手牌
    currentPlayerNumber = -1
    for index, player in poker_table.players:
        if player == wallet_address:
            currentPlayerNumber = index
    # 返回所属队伍
    if wallet_address in poker_table.teamAPlayers:
        team = "A"
    else:
        team = "B"
    # 两支队伍的等级与当前级牌直接确定为2，因为是第一幅牌
    return True, games_id, poker_table.playerCards[currentPlayerNumber], team, outCardRight
    return False, -1, [], "", False'''


def get_suit_and_value(card):
    # 处理特殊牌
    if card in ['bigjoker', 'smalljoker']:
        return card, card
    # 通过正则表达式提取花色和点数
    match = re.match(r"([^0-9]+)([0-9JQKA]+)", card)
    suit, value = match.groups()
    return suit, value


def is_consecutive(values):
    """检查列表中的值是否连续"""
    return all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1))


def classify_cards(cards, gradeCard):
    if len(cards) == 0:
        return "空牌", None, None
    if len(cards) > 6:
        return "未知牌型", None, None

    suits, values = zip(*(get_suit_and_value(card) for card in cards))
    values_counter = Counter(values)
    print(values_counter)
    suits_counter = Counter(suits)

    # 天王炸判断
    if values_counter == Counter({'bigjoker': 2, 'smalljoker': 2}):
        return "天王炸", None, None

    # 点数映射到整数以便比较
    value_map_with_grade = {str(i): i for i in range(2, 11)}
    value_map_with_grade.update({'J': 11, 'Q': 12, 'K': 13, 'A': 14, 'smalljoker': 16, 'bigjoker': 17})
    value_map_with_grade.update({str(gradeCard): 15})
    value_map_without_grade = {str(i): i for i in range(2, 11)}
    value_map_without_grade.update({'J': 11, 'Q': 12, 'K': 13, 'A': 14, 'smalljoker': 16, 'bigjoker': 17})

    sorted_values_with_grade = sorted(
        [value_map_with_grade[value] for value in values if value in value_map_with_grade])
    print(sorted_values_with_grade)
    unique_sorted_values_with_grade = sorted(set(sorted_values_with_grade))
    print(unique_sorted_values_with_grade)
    min_value_with_grade = min(unique_sorted_values_with_grade) if unique_sorted_values_with_grade else None

    sorted_values_without_grade = sorted(
        [value_map_without_grade[value] for value in values if value in value_map_without_grade])
    print(sorted_values_without_grade)
    unique_sorted_values_without_grade = sorted(set(sorted_values_without_grade))
    print(unique_sorted_values_without_grade)
    min_value_without_grade = min(unique_sorted_values_without_grade) if unique_sorted_values_without_grade else None

    # 炸弹判断
    if len(values_counter) == 1 and values_counter[list(values_counter.keys())[0]] >= 4:
        return "炸弹", min_value_with_grade, list(values_counter.keys())[0]
    # 同花顺判断
    if len(suits_counter) == 1 and is_consecutive(sorted_values_without_grade) and len(cards) == 5:
        return "同花顺", min_value_without_grade, None
    # 顺子判断
    if is_consecutive(sorted_values_without_grade) and len(cards) == 5:
        return "顺子", min_value_without_grade, None
    # 三带二判断
    if sorted(values_counter.values()) == [2, 3]:
        keys_with_count_three = [key for key, count in values_counter.items() if count == 3]
        min_3_2 = value_map_with_grade[keys_with_count_three[0]]
        return "三带二", min_3_2, None
    # 二连三判断
    if len(cards) == 6 and sorted(values_counter.values()) == [3, 3] and is_consecutive(sorted_values_without_grade):
        return "二连三", min_value_without_grade, None
    # 三连对判断
    if len(cards) == 6 and all(value == 2 for value in values_counter.values()) and is_consecutive(
            sorted_values_without_grade):
        return "三连对", min_value_without_grade, None
    # 三同张判断
    if 3 in values_counter.values() and len(cards) == 3:
        return "三同张", min_value_with_grade, None
    # 对子判断
    if len(cards) == 2 and len(values_counter) == 1:
        return "对子", min_value_with_grade, None
    # 单张判断
    if len(cards) == 1:
        return "单张", min_value_with_grade, None

    return "未知牌型", None, None


def checkValid(outedCards, gradeCard):
    outed_type, _, _ = classify_cards(outedCards, gradeCard)
    outed_type = CardsType[outed_type]
    if outed_type == "Unknown":
        return False
    else:
        return True


def checkOverField(outedCards, fieldCards, gradeCard):
    outed_type, outed_min_value, outed_bombNum = classify_cards(outedCards, gradeCard)
    # outed_type = CardsType[outed_type]
    field_type, field_min_value, field_bombNum = classify_cards(fieldCards, gradeCard)
    # field_type = CardsType[field_type]
    # 第二种情况：OutedCards为特殊牌型
    if outed_type in ["炸弹", "天王炸", "天王炸"]:
        if field_type not in ["炸弹", "天王炸", "同花顺"]:
            return True  # 特殊牌型压制非特殊牌型
        else:
            # 特殊牌型之间比较基准点数
            if outed_type == "天王炸" and field_type == "炸弹":
                return True
            elif outed_type == "天王炸" and field_type == "同花顺":
                return True
            elif outed_type == "炸弹" and field_type == "天王炸":
                return False
            elif outed_type == "炸弹" and field_type == "同花顺":
                if outed_bombNum <= 5:
                    return False
                elif outed_bombNum == 6:
                    return True
            elif outed_type == "炸弹" and field_type == "炸弹":
                if outed_bombNum > field_bombNum:
                    return True
                elif outed_bombNum < field_bombNum:
                    return False
                else:
                    return outed_min_value > field_min_value
            elif outed_type == "同花顺" and field_type == "天王炸":
                return False
            elif outed_type == "同花顺" and field_type == "同花顺":
                return outed_min_value > field_min_value
            elif outed_type == "同花顺" and field_type == "炸弹":
                if field_bombNum <= 5:
                    return True
                elif field_bombNum == 6:
                    return False
    # 第一种情况：OutedCards非特殊牌型，需要牌型相同并且比较基准点数
    if outed_type == field_type and outed_min_value > field_min_value:
        return True
    return False


def dealRank(pokerTable, wallet_address):
    # 判定该玩家本副牌排名
    max_rank = -2
    has_rank_count = 0
    teamA_ranked_count = 0
    teamB_ranked_count = 0
    curWallAddrTeam = ""
    if wallet_address in pokerTable.teamAPlayers:
        curWallAddrTeam = "A"
    else:
        curWallAddrTeam = "B"
    championPlayer = ""
    for playerAddr, rank in pokerTable.currentGamePositions:
        if rank != -1 & rank > max_rank:
            max_rank = rank
            has_rank_count += 1
            if rank == 1:
                championPlayer = playerAddr
            if playerAddr in pokerTable.teamAPlayers:
                teamA_ranked_count += 1
            elif playerAddr in pokerTable.teamBPlayers:
                teamB_ranked_count += 1
            else:
                print("Invalid playerAddr ! rank round")
    # 已有2个出完牌,现在第三名玩家出完牌，意味着游戏必定结束
    if has_rank_count == 2 & max_rank == 2:
        # 先定排名 3 和 4
        pokerTable.currentGamePositions[wallet_address] = 3
        if wallet_address in pokerTable.teamAPlayers:
            teamA_ranked_count += 1
        elif wallet_address in pokerTable.teamBplayers:
            teamB_ranked_count += 1
        else:
            print("Invalid playerAddr ! rank round")

        # 处理本副牌胜利结果
        for playerAddr, rank in pokerTable.currentGamePositions:
            if rank == -1:
                pokerTable[playerAddr] = 4

        # 处理升级， 决定最终胜利 teamWinAll
        if championPlayer in pokerTable.teamAPlayers:
            # 本副牌 A 胜利 teamA 升级
            pokerTable.lastWinTeam = "A"
            for pAddr in pokerTable.teamAPlayers:
                if pAddr != championPlayer:
                    pokerTable.teamAGrade += 5 - pokerTable.currentGamePositions[pAddr]
                    if pokerTable.teamAGrade == 14 | pokerTable.teamAGrade > 14:
                        # 出现最终胜利结果
                        pokerTable.winAllTeam = "A"
        else:
            # 本副牌 B 胜利 teamB 升级
            pokerTable.lastWinTeam = "B"
            for pAddr in pokerTable.teamBPlayers:
                if pAddr != championPlayer:
                    pokerTable.teamBGrade += 5 - pokerTable.currentGamePositions[pAddr]
                    if pokerTable.teamBGrade == 14 | pokerTable.teamBGrade > 14:
                        # 出现最终胜利结果
                        pokerTable.winAllTeam = "B"

        # 处理本局牌结果
        pokerTable.currentRound += 1
        # 如果到达最大局数
        '''
        if pokerTable.currentRound == pokerTable.maxRounds:
            # 到达最大局数，直接定生死
            if pokerTable.teamAGrade != 1 & pokerTable.teamBGrade != 1:
                # A赢了
                if pokerTable.teamAGrade > pokerTable.teamBGrade:
                    pokerTable.winAllTeam = "A"
                else:
                    pokerTable.winAllTeam = "B"
            elif pokerTable.teamAGrade == 1 & pokerTable.teamBGrade == 1:
                # 2队都打到A，点数相同
                # 理想：加赛一局定生死 现实：直接平局处理
                pokerTable.winAllTeam = "AB"
            else:
                if pokerTable.teamAGrade == 1:
                    pokerTable.winAllTeam = "A"
                else:
                    pokerTable.winAllTeam = "B"
        '''
        # 未到达最大局数
        # 阉割 不设置最大局数
        # 下一副牌开始时需要根据本副牌排名处理贡牌
        pokerTable.lastGamePositionsGame = pokerTable.currentGamePositions
        # pokerTable.lastWinTeam 前面已经处理过了
    # 已有1个玩家出完牌,现在第3名玩家出完牌，意味着游戏可能结束，若结束就是双上游，直接定另外两名玩家排名为4,4
    elif has_rank_count == 1 & max_rank == 1:
        if championPlayer in pokerTable.teamAPlayers & curWallAddrTeam == "A":
            # A双上游获胜
            pokerTable.currentGamePositions[wallet_address] = 2
            for pAddr, rank in pokerTable.currentGamePositions:
                if rank == -1:
                    pokerTable.currentGamePositions[pAddr] = 4
            pokerTable.winAllTeam = "A"
            pokerTable.lastWinTeam = "A"
            pokerTable.lastGamePositions = pokerTable.currentGamePositions
        elif championPlayer in pokerTable.teamBPlayers & curWallAddrTeam == "B":
            # B双上游获胜
            pokerTable.currentGamePositions[wallet_address] = 2
            for pAddr, rank in pokerTable.currentGamePositions:
                if rank == -1:
                    pokerTable.currentPositions[pAddr] = 4
            pokerTable.winAllTeam = "B"
            pokerTable.lastWinTeam = "B"
            pokerTable.lastGamePositions = pokerTable.currentGamePositions
        else:
            # 没有最终结果,说明第一第二分别属于两支队伍
            pokerTable.currentGamePositions[wallet_address] = 2
    else:
        # 此时当前玩家为第一个出完手牌的,不会产生胜负
        pokerTable.currentGamePositions[wallet_address] = 1
    # 需要返回给前端的信息：
    # 当前玩家出完牌获得第几游，本副牌是否出现胜负lastWinTeam，是否出现最终胜利结果WinAll
    getPos = pokerTable.currentGamePositions[wallet_address]
    getSingleWin = pokerTable.lastWinTeam
    getAllWin = pokerTable.winAllTeam
    return getPos, getSingleWin, getAllWin
