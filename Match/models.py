from django.db import models

# Create your models here.
from django.db import models


# Create your models here.

class PokerTable:
    def __init__(self):
        # 全局信息
        self.game_id = 0
        self.players = ["", "", "", ""]
        self.teamAPlayers = [self.players[0], self.players[1]]
        self.teamBPlayers = [self.players[2], self.players[3]]
        self.teamAGrade = 2
        self.teamBGrade = 2
        self.currentGrade = 2
        self.maxRounds = 10  # 假设一局最多10副牌
        self.currentRound = 0
        self.winAllTeam = ""

        # 单副牌信息
        self.currentHand = ""
        self.lastWinTeam = ""
        self.lastGamePositions = {self.players[0]: -1, self.players[1]: -1, self.players[2]: -1, self.players[3]: -1}
        self.currentGamePositions = {self.players[0]: -1, self.players[1]: -1, self.players[2]: -1, self.players[3]: -1}
        self.playerCards = {self.players[0]: [], self.players[1]: [], self.players[2]: [], self.players[3]: []}
        self.FieldCard = ""

    # 添加其他方法来处理游戏逻辑
