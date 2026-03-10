from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List, Callable, Dict, Any, Tuple

class JokerRarity(Enum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    LEGENDARY = auto()

class JokerEvent(Enum):
    ON_JOKER_CREATED = auto()       # 创建时触发 (初始化)
    ON_HAND_PLAYED = auto()         # 手牌打出前 (计算手牌类型后)
    ON_CARD_SCORED = auto()         # 计分卡牌计分时
    ON_CARD_SCORED_END = auto()     # 计分卡牌计分后 (Retrigger)
    ON_CARD_HELD = auto()           # 手牌持有时 (Steel Card / Baron等)
    INDEPENDENT = auto()            # 独立触发 (通常在计分卡牌后，计算 Joker 倍率)
    ON_HAND_SCORED_END = auto()     # 整手牌计分结束 (Food Jokers, etc.)
    ON_HAND_DISCARDED = auto()      # 弃牌时
    ON_ROUND_END = auto()           # 回合结束
    ON_BLIND_SELECTED = auto()      # 盲注选择时

@dataclass
class JokerEffect:
    chips: int = 0
    mult: int = 0
    xmult: float = 0.0
    money: int = 0
    retrigger: bool = False
    expire: bool = False
    message: Optional[str] = None

class Joker:
    def __init__(self, id: int, name: str, name_cn: str, rarity: JokerRarity, cost: int, effect_func: Callable, desc: str = ""):
        self.id = id
        self.name = name
        self.name_cn = name_cn
        self.rarity = rarity
        self.cost = cost
        self.effect_func = effect_func
        self.desc = desc # 详细描述
        
        # 运行时状态
        self.scoring_state: Any = None
        self.persistent_state: Any = None

    def trigger(self, scored_card: Any, event: JokerEvent, context: Dict[str, Any] = None) -> Optional[JokerEffect]:
        """触发 Joker 效果"""
        return self.effect_func(self, scored_card, event, context)

    def __str__(self):
        return f"{self.name} ({self.name_cn})"
