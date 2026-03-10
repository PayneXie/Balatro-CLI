from enum import Enum, auto
from typing import Any, Optional

class ShopItemType(Enum):
    JOKER = auto()
    TAROT = auto()
    PLANET = auto()
    PACK = auto()
    VOUCHER = auto()

class ShopItem:
    def __init__(self, type: ShopItemType, price: int, payload: Any):
        self.type = type
        self.price = price
        self.payload = payload  # Joker, Consumable, or Pack type string
        self.is_bought = False

    @property
    def name(self) -> str:
        if self.type in (ShopItemType.JOKER, ShopItemType.TAROT, ShopItemType.PLANET):
            return self.payload.name
        elif self.type == ShopItemType.PACK:
            return f"{self.payload} Pack"
        elif self.type == ShopItemType.VOUCHER:
            return self.payload # Placeholder for Voucher object
        return "Unknown"

    @property
    def name_cn(self) -> str:
        if self.type in (ShopItemType.JOKER, ShopItemType.TAROT, ShopItemType.PLANET):
            return self.payload.name_cn
        elif self.type == ShopItemType.PACK:
            # Simple translation map
            cn_map = {
                'Arcana': '塔罗包',
                'Celestial': '星球包',
                'Standard': '扑克包',
                'Buffoon': '小丑包'
            }
            return cn_map.get(self.payload, self.payload)
        return self.name

    @property
    def desc(self) -> str:
        if self.type in (ShopItemType.JOKER, ShopItemType.TAROT, ShopItemType.PLANET):
            return getattr(self.payload, 'desc', "")
        elif self.type == ShopItemType.PACK:
            desc_map = {
                'Arcana': '包含塔罗牌',
                'Celestial': '包含星球牌',
                'Standard': '包含扑克牌',
                'Buffoon': '包含小丑牌'
            }
            return desc_map.get(self.payload, "卡包")
        return ""
