from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    BLIND_SELECT = auto()
    PLAYING = auto()
    ROUND_END = auto()
    SHOP = auto()
    PACK_OPEN = auto() # 卡包开启状态
    DECK_VIEW = auto() # 查看牌组状态
    GAME_OVER = auto()
    WIN = auto()

class BlindType(Enum):
    SMALL = auto()
    BIG = auto()
    BOSS = auto()
