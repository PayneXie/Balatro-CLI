from enum import Enum, auto
from typing import List, Callable, Optional, Dict, Any
from .card import Card, CardType, CardEdition

class ConsumableType(Enum):
    PLANET = auto()
    TAROT = auto()

class Consumable:
    def __init__(self, id: int, name: str, name_cn: str, type: ConsumableType, cost: int, effect_func: Callable, desc: str = ""):
        self.id = id
        self.name = name
        self.name_cn = name_cn
        self.type = type
        self.cost = cost
        self.effect_func = effect_func
        self.desc = desc

    def use(self, game: Any, target_card: Optional[Card] = None) -> bool:
        """使用消耗品"""
        return self.effect_func(self, game, target_card)

    def __str__(self):
        return f"{self.name} ({self.name_cn})"

# --- Effect Functions ---

def effect_planet_mercury(consumable: Consumable, game: Any, target: Any) -> bool:
    # 对应 Pair
    from .hand_analysis import HandType
    return game.upgrade_hand(HandType.PAIR)

def effect_planet_venus(consumable: Consumable, game: Any, target: Any) -> bool:
    # 对应 Three of a Kind
    from .hand_analysis import HandType
    return game.upgrade_hand(HandType.THREE_OF_A_KIND)

def effect_planet_earth(consumable: Consumable, game: Any, target: Any) -> bool:
    # 对应 Full House
    from .hand_analysis import HandType
    return game.upgrade_hand(HandType.FULL_HOUSE)

def effect_planet_mars(consumable: Consumable, game: Any, target: Any) -> bool:
    # 对应 Four of a Kind
    from .hand_analysis import HandType
    return game.upgrade_hand(HandType.FOUR_OF_A_KIND)

def effect_planet_jupiter(consumable: Consumable, game: Any, target: Any) -> bool:
    # 对应 Flush
    from .hand_analysis import HandType
    return game.upgrade_hand(HandType.FLUSH)

def effect_planet_saturn(consumable: Consumable, game: Any, target: Any) -> bool:
    # 对应 Straight
    from .hand_analysis import HandType
    return game.upgrade_hand(HandType.STRAIGHT)

def effect_tarot_fool(consumable: Consumable, game: Any, target: Any) -> bool:
    # 愚者：复制上一个使用的消耗品（简化：随机给一个）
    import random
    new_consumable = create_consumable(random.choice([0, 1, 2, 3, 4, 5]))
    if len(game.consumables) < game.max_consumables:
        game.consumables.append(new_consumable)
        return True
    return False

def effect_tarot_magician(consumable: Consumable, game: Any, target: Card) -> bool:
    # 魔术师：将 1 张牌变为幸运牌
    if target:
        target.enhancement = CardType.LUCKY
        return True
    return False

def effect_tarot_empress(consumable: Consumable, game: Any, target: Card) -> bool:
    # 皇后：将 1 张牌变为倍率牌
    if target:
        target.enhancement = CardType.MULT
        return True
    return False

def effect_tarot_hierophant(consumable: Consumable, game: Any, target: Card) -> bool:
    # 教皇：将 1 张牌变为奖励牌
    if target:
        target.enhancement = CardType.BONUS
        return True
    return False

def effect_tarot_chariot(consumable: Consumable, game: Any, target: Card) -> bool:
    # 战车：将 1 张牌变为钢铁牌
    if target:
        target.enhancement = CardType.STEEL
        return True
    return False

def effect_tarot_justice(consumable: Consumable, game: Any, target: Card) -> bool:
    # 正义：将 1 张牌变为玻璃牌
    if target:
        target.enhancement = CardType.GLASS
        return True
    return False

# --- Registry ---

CONSUMABLE_DEFINITIONS = [
    # ID, Name, NameCN, Type, Cost, EffectFunc, Desc
    (0, "Mercury", "水星", ConsumableType.PLANET, 3, effect_planet_mercury, "升级 对子"),
    (1, "Venus", "金星", ConsumableType.PLANET, 3, effect_planet_venus, "升级 三条"),
    (2, "Earth", "地球", ConsumableType.PLANET, 3, effect_planet_earth, "升级 葫芦"),
    (3, "Mars", "火星", ConsumableType.PLANET, 3, effect_planet_mars, "升级 四条"),
    (4, "Jupiter", "木星", ConsumableType.PLANET, 3, effect_planet_jupiter, "升级 同花"),
    (5, "Saturn", "土星", ConsumableType.PLANET, 3, effect_planet_saturn, "升级 顺子"),
    
    (10, "The Magician", "魔术师", ConsumableType.TAROT, 3, effect_tarot_magician, "将1张牌变为 幸运牌"),
    (11, "The Empress", "皇后", ConsumableType.TAROT, 3, effect_tarot_empress, "将1张牌变为 倍率牌 (+4 Mult)"),
    (12, "The Hierophant", "教皇", ConsumableType.TAROT, 3, effect_tarot_hierophant, "将1张牌变为 奖励牌 (+30 Chips)"),
    (13, "The Chariot", "战车", ConsumableType.TAROT, 3, effect_tarot_chariot, "将1张牌变为 钢铁牌 (手持x1.5 Mult)"),
    (14, "The Justice", "正义", ConsumableType.TAROT, 3, effect_tarot_justice, "将1张牌变为 玻璃牌 (x2 Mult, 1/4几率自毁)"),
]

def create_consumable(consumable_id: int) -> Optional[Consumable]:
    for definition in CONSUMABLE_DEFINITIONS:
        if definition[0] == consumable_id:
            return Consumable(*definition)
    return None

def get_all_consumables() -> List[Consumable]:
    return [create_consumable(d[0]) for d in CONSUMABLE_DEFINITIONS]
