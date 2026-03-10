from typing import Optional, List
from .joker import Joker, JokerEffect, JokerEvent, JokerRarity
from .card import Card, Suit, Rank, CardType

# --- Helper Functions ---

def _is_suit(card: Card, suit: Suit) -> bool:
    return card.suit == suit

def _is_face_card(card: Card) -> bool:
    return card.rank in (Rank.JACK, Rank.QUEEN, Rank.KING)

# --- Joker Implementations ---

def joker_effect_gros_michel(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Gros Michel: +15 Mult. 1 in 4 chance to be destroyed at end of round.
    if event == JokerEvent.INDEPENDENT:
        return JokerEffect(mult=15)
    
    if event == JokerEvent.ON_ROUND_END:
        import random
        if random.random() < 0.25:
            return JokerEffect(expire=True, message="Extinct!")
            
    return None

def joker_effect_greedy_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Greedy Joker: Played cards with Diamond suit give +4 Mult when scored
    if event == JokerEvent.ON_CARD_SCORED and scored_card and _is_suit(scored_card, Suit.DIAMONDS):
        return JokerEffect(mult=4)
    return None

def joker_effect_lusty_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Lusty Joker: Played cards with Heart suit give +4 Mult when scored
    if event == JokerEvent.ON_CARD_SCORED and scored_card and _is_suit(scored_card, Suit.HEARTS):
        return JokerEffect(mult=4)
    return None

def joker_effect_wrathful_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Wrathful Joker: Played cards with Spade suit give +4 Mult when scored
    if event == JokerEvent.ON_CARD_SCORED and scored_card and _is_suit(scored_card, Suit.SPADES):
        return JokerEffect(mult=4)
    return None

def joker_effect_gluttonous_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Gluttonous Joker: Played cards with Club suit give +4 Mult when scored
    if event == JokerEvent.ON_CARD_SCORED and scored_card and _is_suit(scored_card, Suit.CLUBS):
        return JokerEffect(mult=4)
    return None

def joker_effect_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Joker (Base): +4 Mult
    if event == JokerEvent.INDEPENDENT:
        return JokerEffect(mult=4)
    return None

def joker_effect_jolly_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Jolly Joker: +8 Mult if played hand contains a Pair
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        # Simple check - in real game this checks "contained" hands
        # For now we assume context has 'hand_type'
        # To be fully accurate we need to check if the hand *contains* a pair, not just *is* a pair
        # But based on sample code: "if (get_contained_hands()->PAIR)"
        # We will need to pass contained hands info. For now, simplify:
        if hand_type and hand_type.name in ('PAIR', 'TWO_PAIR', 'FULL_HOUSE', 'FOUR_OF_A_KIND'): 
             return JokerEffect(mult=8)
    return None

def joker_effect_zany_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Zany Joker: +12 Mult if played hand contains a Three of a Kind
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('THREE_OF_A_KIND', 'FULL_HOUSE', 'FOUR_OF_A_KIND'):
            return JokerEffect(mult=12)
    return None

def joker_effect_mad_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Mad Joker: +10 Mult if played hand contains a Two Pair
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('TWO_PAIR',):
             return JokerEffect(mult=10)
    return None

def joker_effect_crazy_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Crazy Joker: +12 Mult if played hand contains a Straight
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('STRAIGHT', 'STRAIGHT_FLUSH', 'ROYAL_FLUSH'):
             return JokerEffect(mult=12)
    return None

def joker_effect_droll_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Droll Joker: +10 Mult if played hand contains a Flush
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('FLUSH', 'STRAIGHT_FLUSH', 'ROYAL_FLUSH'):
             return JokerEffect(mult=10)
    return None

def joker_effect_sly_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Sly Joker: +50 Chips if played hand contains a Pair
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('PAIR', 'TWO_PAIR', 'FULL_HOUSE', 'FOUR_OF_A_KIND'): 
             return JokerEffect(chips=50)
    return None

def joker_effect_wily_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Wily Joker: +100 Chips if played hand contains a Three of a Kind
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('THREE_OF_A_KIND', 'FULL_HOUSE', 'FOUR_OF_A_KIND'):
            return JokerEffect(chips=100)
    return None

def joker_effect_clever_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Clever Joker: +80 Chips if played hand contains a Two Pair
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('TWO_PAIR',):
             return JokerEffect(chips=80)
    return None

def joker_effect_devious_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Devious Joker: +100 Chips if played hand contains a Straight
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('STRAIGHT', 'STRAIGHT_FLUSH', 'ROYAL_FLUSH'):
             return JokerEffect(chips=100)
    return None

def joker_effect_crafty_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Crafty Joker: +80 Chips if played hand contains a Flush
    if event == JokerEvent.INDEPENDENT:
        hand_type = context.get('hand_type')
        if hand_type and hand_type.name in ('FLUSH', 'STRAIGHT_FLUSH', 'ROYAL_FLUSH'):
             return JokerEffect(chips=80)
    return None

def joker_effect_half_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Half Joker: +20 Mult if played hand has 3 or fewer cards
    if event == JokerEvent.INDEPENDENT:
        played_cards = context.get('played_cards', [])
        if len(played_cards) <= 3:
            return JokerEffect(mult=20)
    return None

def joker_effect_stencil_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Joker Stencil: X1 Mult for each empty Joker slot
    if event == JokerEvent.INDEPENDENT:
        jokers = context.get('jokers', [])
        max_jokers = context.get('max_jokers', 5)
        # Count stencils (including self) to add extra
        # Logic from sample: (MAX - current) + stencils_count
        # But sample says: "xmult = (MAX_JOKERS_HELD_SIZE)-num_jokers"
        # And then: "each stencil_joker adds +1 xmult"
        # Wait, if I have 1 stencil and 4 empty slots. num_jokers=1. MAX=5. 5-1 = 4. +1 (self) = X5.
        
        # Let's simplify: 1X per empty slot. Stencil itself takes a slot but includes itself in the bonus essentially?
        # Actually Stencil says: "X1 Mult for each empty Joker slot. Joker Stencil included"
        # So if I have 1 Stencil and 4 empty slots -> 4 empty + 1 Stencil = X5.
        
        empty_slots = max_jokers - len(jokers)
        # Check how many stencils are in the joker list? 
        # Actually we just return the multiplier for THIS joker.
        # This joker gives X(1 * empty_slots + 1) ?
        # No, Stencil gives a total XMult based on game state.
        
        # Re-reading sample:
        # (*joker_effect)->xmult = (MAX_JOKERS_HELD_SIZE)-num_jokers;
        # ...
        # if (joker_object->joker->id == STENCIL_JOKER_ID) (*joker_effect)->xmult++;
        
        # So for *each* stencil, it adds XMult = (Empty Slots + Count of Stencils)?
        # Wait, the sample loop adds +1 for *each* stencil found in the list to the effect of *this* stencil.
        # That seems to imply Stencil Stacking? 
        
        # Let's stick to the official text: "X1 Mult for each empty Joker slot. Joker Stencil included."
        # This usually means X(Empty + 1).
        
        return JokerEffect(xmult=empty_slots + 1)
    return None

def joker_effect_bull(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Bull: +2 Chips for each dollar you have
    if event == JokerEvent.INDEPENDENT:
        money = context.get('money', 0)
        if money > 0:
            return JokerEffect(chips=money * 2)
    return None

def joker_effect_popcorn(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Popcorn: +20 Mult. -4 Mult per round played.
    if event == JokerEvent.ON_JOKER_CREATED:
        joker.scoring_state = 20 # Initialize mult
        
    if event == JokerEvent.INDEPENDENT:
        if joker.scoring_state is None: joker.scoring_state = 20
        return JokerEffect(mult=joker.scoring_state)
        
    if event == JokerEvent.ON_ROUND_END:
        if joker.scoring_state is None: joker.scoring_state = 20
        joker.scoring_state -= 4
        if joker.scoring_state <= 0:
            return JokerEffect(expire=True, message="Eaten!")
        return JokerEffect(message=f"{joker.scoring_state} Mult")
            
    return None

def joker_effect_gros_michel(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Gros Michel: +15 Mult. 1 in 4 chance to be destroyed at end of round.
    if event == JokerEvent.INDEPENDENT:
        return JokerEffect(mult=15)
    
    if event == JokerEvent.ON_ROUND_END:
        import random
        if random.random() < 0.25:
            return JokerEffect(expire=True, message="Extinct!")
            
    return None

def joker_effect_ice_cream(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Ice Cream: +100 Chips. -5 Chips for every hand played.
    if event == JokerEvent.ON_JOKER_CREATED:
        joker.scoring_state = 100
        
    if event == JokerEvent.INDEPENDENT:
        if joker.scoring_state is None: joker.scoring_state = 100
        return JokerEffect(chips=joker.scoring_state)
        
    if event == JokerEvent.ON_HAND_PLAYED:
        if joker.scoring_state is None: joker.scoring_state = 100
        joker.scoring_state -= 5
        if joker.scoring_state <= 0:
             return JokerEffect(expire=True, message="Melted!")
             
    return None

def joker_effect_blue_joker(joker: Joker, scored_card: Card, event: JokerEvent, context: dict) -> Optional[JokerEffect]:
    # Blue Joker: +2 Chips for each remaining card in deck
    if event == JokerEvent.INDEPENDENT:
        deck_size = context.get('deck_size', 0)
        return JokerEffect(chips=deck_size * 2)
    return None

# --- Joker Registry ---

# ID, Name, NameCN, Rarity, Cost, EffectFunc, Desc
JOKER_DEFINITIONS = [
    (0, "Joker", "小丑", JokerRarity.COMMON, 2, joker_effect_joker, "+4 倍率"),
    (1, "Greedy Joker", "贪婪小丑", JokerRarity.COMMON, 5, joker_effect_greedy_joker, "打出方块牌时 +4 倍率"),
    (2, "Lusty Joker", "色欲小丑", JokerRarity.COMMON, 5, joker_effect_lusty_joker, "打出红桃牌时 +4 倍率"),
    (3, "Wrathful Joker", "暴怒小丑", JokerRarity.COMMON, 5, joker_effect_wrathful_joker, "打出黑桃牌时 +4 倍率"),
    (4, "Gluttonous Joker", "暴食小丑", JokerRarity.COMMON, 5, joker_effect_gluttonous_joker, "打出梅花牌时 +4 倍率"),
    (5, "Jolly Joker", "开心小丑", JokerRarity.COMMON, 3, joker_effect_jolly_joker, "牌型包含对子时 +8 倍率"),
    (6, "Zany Joker", "滑稽小丑", JokerRarity.COMMON, 4, joker_effect_zany_joker, "牌型包含三条时 +12 倍率"),
    (7, "Mad Joker", "疯狂小丑", JokerRarity.COMMON, 4, joker_effect_mad_joker, "牌型包含两对时 +10 倍率"),
    (8, "Crazy Joker", "癫狂小丑", JokerRarity.COMMON, 4, joker_effect_crazy_joker, "牌型包含顺子时 +12 倍率"),
    (9, "Droll Joker", "滑稽小丑", JokerRarity.COMMON, 4, joker_effect_droll_joker, "牌型包含同花时 +10 倍率"),
    (10, "Sly Joker", "狡猾小丑", JokerRarity.COMMON, 3, joker_effect_sly_joker, "牌型包含对子时 +50 筹码"),
    (11, "Wily Joker", "诡计小丑", JokerRarity.COMMON, 4, joker_effect_wily_joker, "牌型包含三条时 +100 筹码"),
    (12, "Clever Joker", "聪阴小丑", JokerRarity.COMMON, 4, joker_effect_clever_joker, "牌型包含两对时 +80 筹码"),
    (13, "Devious Joker", "迂回小丑", JokerRarity.COMMON, 4, joker_effect_devious_joker, "牌型包含顺子时 +100 筹码"),
    (14, "Crafty Joker", "工匠小丑", JokerRarity.COMMON, 4, joker_effect_crafty_joker, "牌型包含同花时 +80 筹码"),
    (15, "Half Joker", "半个小丑", JokerRarity.COMMON, 5, joker_effect_half_joker, "打出牌数<=3时 +20 倍率"),
    (16, "Joker Stencil", "小丑模版", JokerRarity.UNCOMMON, 8, joker_effect_stencil_joker, "每个空Joker槽位 X1 倍率"),
    (17, "Bull", "公牛", JokerRarity.UNCOMMON, 6, joker_effect_bull, "每拥有 $1 增加 +2 筹码"),
    (18, "Popcorn", "爆米花", JokerRarity.COMMON, 5, joker_effect_popcorn, "+20 倍率，每回合 -4 倍率"),
    (19, "Gros Michel", "大麦克", JokerRarity.COMMON, 5, joker_effect_gros_michel, "+15 倍率，每回合 1/4 几率自毁"),
    (20, "Ice Cream", "冰淇淋", JokerRarity.COMMON, 5, joker_effect_ice_cream, "+100 筹码，每出牌 -5 筹码"),
    (21, "Blue Joker", "蓝色小丑", JokerRarity.COMMON, 5, joker_effect_blue_joker, "牌库每剩1张牌 +2 筹码"),
]

def create_joker(joker_id: int) -> Optional[Joker]:
    for definition in JOKER_DEFINITIONS:
        if definition[0] == joker_id:
            joker = Joker(*definition)
            # Init hook
            joker.trigger(None, JokerEvent.ON_JOKER_CREATED)
            return joker
    return None

def get_all_jokers() -> List[Joker]:
    # 过滤掉不存在的 joker_id，避免 create_joker 返回 None 导致列表含 None
    jokers = []
    for d in JOKER_DEFINITIONS:
        j = create_joker(d[0])
        if j:
            jokers.append(j)
    return jokers
