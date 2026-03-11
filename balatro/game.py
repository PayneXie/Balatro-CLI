from typing import List, Optional, Dict, Any, Tuple
from .card import Card, CardType
from .deck import Deck, DeckType
from .enums import GameState, BlindType
from .blind import Blind
from .hand_analysis import HandEvaluator, HandType
from .joker import Joker, JokerEvent, JokerEffect
from .consumable import Consumable, ConsumableType
from .shop import ShopItem, ShopItemType

class Game:
    def __init__(self):
        # 基础状态
        self.state = GameState.MAIN_MENU
        self.deck_type = DeckType.RED # Default
        self.deck = Deck(self.deck_type)
        self.hand: List[Card] = []
        self.jokers: List[Joker] = [] # 当前拥有的 Joker
        self.consumables: List[Consumable] = [] # 当前拥有的消耗品
        self.discards_remaining = 0
        self.hands_remaining = 0
        self.money = 0
        self.ante = 1
        self.round = 0
        self.current_blind_type = BlindType.SMALL
        self.current_blind: Optional[Blind] = None
        self.current_score = 0
        self.target_score = 0
        
        # 商店相关 (重构为分区架构)
        self.joker_slots: List[ShopItem] = []    # 槽位 1-2: Joker/消耗品
        self.pack_slots: List[ShopItem] = []     # 槽位 3-4: 卡包
        self.voucher_slot: Optional[ShopItem] = None # 槽位 5: 优惠券
        
        self.reroll_cost = 5
        self.reroll_base_cost = 5
        
        # Deck View State
        self.deck_view_selection_mode = False # Whether we are selecting a card for Tarot
        self.selected_consumable_index = -1 # Which consumable initiated the selection
        
        # 牌型等级系统
        # 格式: {HandType: {"level": 1, "chips": 10, "mult": 2}}
        self.hand_levels = self._init_hand_levels()
        
        # 奖励信息 (Round End 使用)
        self.round_reward = 0
        self.interest = 0
        
        # 游戏配置
        self.max_hand_size = 8
        self.max_hands = 4
        self.max_discards = 3 # 默认3次
        self.max_ante = 8
        self.max_interest = 5
        self.interest_per_5 = 1
        self.max_jokers = 5
        self.max_consumables = 2

    @property
    def shop_items(self) -> List[ShopItem]:
        """为了兼容旧 UI，合并所有商店槽位"""
        items = []
        items.extend(self.joker_slots)
        items.extend(self.pack_slots)
        if self.voucher_slot:
            items.append(self.voucher_slot)
        return items

    def _init_shop(self, reset_reroll=True):
        """初始化商店物品 (分区架构实现)"""
        import random
        from .joker_effects import get_all_jokers
        from .consumable import get_all_consumables
        
        if reset_reroll:
            self.reroll_cost = self.reroll_base_cost
        
        # 1. 生成卡牌区 (Joker/Tarot/Planet)
        self.joker_slots = []
        all_jokers = get_all_jokers()
        all_consumables = get_all_consumables()
        
        for _ in range(2):
            if random.random() < 0.7:
                # 70% 概率生成 Joker
                payload = random.choice(all_jokers)
                self.joker_slots.append(ShopItem(ShopItemType.JOKER, payload.cost, payload))
            else:
                # 30% 概率生成消耗品
                payload = random.choice(all_consumables)
                item_type = ShopItemType.PLANET if payload.type == ConsumableType.PLANET else ShopItemType.TAROT
                self.joker_slots.append(ShopItem(item_type, payload.cost, payload))
                
        # 2. 生成卡包区
        self.pack_slots = []
        pack_types = ['Arcana', 'Celestial', 'Standard', 'Buffoon']
        for _ in range(2):
            p_type = random.choice(pack_types)
            self.pack_slots.append(ShopItem(ShopItemType.PACK, 4, p_type))
            
        # 3. 生成优惠券 (如果不重置，则保留之前的)
        if reset_reroll or not self.voucher_slot:
            # 简化实现：先不实现具体 Voucher 逻辑，只放一个占位
            self.voucher_slot = ShopItem(ShopItemType.VOUCHER, 10, "Overstock")

    def buy_item(self, zone_index: int, item_index: int):
        """购买商店物品 (需要指定区域和索引)"""
        shop_item = None
        target_list = None
        
        if zone_index == 0: # Card Zone
            if 0 <= item_index < len(self.joker_slots):
                shop_item = self.joker_slots[item_index]
                target_list = self.joker_slots
        elif zone_index == 1: # Pack Zone
            if 0 <= item_index < len(self.pack_slots):
                shop_item = self.pack_slots[item_index]
                target_list = self.pack_slots
        elif zone_index == 2: # Voucher Zone
            if self.voucher_slot and item_index == 0:
                shop_item = self.voucher_slot
                # Voucher slot handled specially
        
        if not shop_item:
            return

        if self.money >= shop_item.price:
            success = False
            
            if shop_item.type == ShopItemType.JOKER:
                if len(self.jokers) < self.max_jokers:
                    self.jokers.append(shop_item.payload)
                    shop_item.payload.trigger(None, JokerEvent.ON_JOKER_CREATED)
                    success = True
            elif shop_item.type in (ShopItemType.TAROT, ShopItemType.PLANET):
                if len(self.consumables) < self.max_consumables:
                    self.consumables.append(shop_item.payload)
                    success = True
            elif shop_item.type == ShopItemType.PACK:
                # 简化：购买卡包直接随机获得一个里面的物品
                # 实际上应该进入一个 "Pack Selection" 状态
                # 这里先改为进入 PACK_OPEN 状态，展示 3 张卡供选择
                # 但为了快速响应需求 "选择卡牌包的时候应该是一个多选一"
                # 我们需要改变 GameState
                
                self.open_pack(shop_item.payload)
                # 购买成功逻辑稍后处理，因为需要先扣钱？
                # Balatro 是先扣钱再开包
                self.money -= shop_item.price
                if target_list: target_list.remove(shop_item)
                return # 提前返回，因为进入了新状态
                
            elif shop_item.type == ShopItemType.VOUCHER:
                # Voucher 逻辑
                success = True
                self.voucher_slot = None # Remove from slot
                
            if success:
                self.money -= shop_item.price
                if target_list:
                    target_list.remove(shop_item)

    def open_pack(self, pack_type: str):
        """打开卡包，生成选项"""
        import random
        from .joker_effects import get_all_jokers
        from .consumable import get_all_consumables, ConsumableType
        from .card import Card, Suit, Rank
        from .shop import ShopItem, ShopItemType 
        
        self.pack_choices = []
        self.state = GameState.PACK_OPEN
        
        # Generate 3 choices based on pack type
        if pack_type == 'Buffoon': # Jokers
            all_jokers = get_all_jokers()
            choices = random.sample(all_jokers, min(3, len(all_jokers)))
            for c in choices:
                self.pack_choices.append(ShopItem(ShopItemType.JOKER, 0, c)) # Price 0 as already paid
                
        elif pack_type == 'Arcana': # Tarot
            all_tarots = [c for c in get_all_consumables() if c.type == ConsumableType.TAROT]
            choices = random.sample(all_tarots, min(3, len(all_tarots)))
            for c in choices:
                self.pack_choices.append(ShopItem(ShopItemType.TAROT, 0, c))
                
        elif pack_type == 'Celestial': # Planet
            all_planets = [c for c in get_all_consumables() if c.type == ConsumableType.PLANET]
            choices = random.sample(all_planets, min(3, len(all_planets)))
            for c in choices:
                self.pack_choices.append(ShopItem(ShopItemType.PLANET, 0, c))
                
        elif pack_type == 'Standard': # Playing Cards
            # Generate random cards with enhancements
            for _ in range(3):
                # Random card
                card = Card(random.choice(list(Suit)), random.choice(list(Rank)))
                
                # 30% chance for enhancement
                if random.random() < 0.3:
                    # Random enhancement (skip BASE, STONE is 1)
                    # Simple way: choice from CardType 1-8
                    import random as rnd # Ensure random is available
                    enh_type = CardType(rnd.randint(1, 8))
                    card.enhancement = enh_type
                    
                # 10% chance for edition (independent)
                if random.random() < 0.1:
                    from .card import CardEdition
                    # Random edition 1-3 (skip NEGATIVE for now as it's rare/special)
                    card.edition = CardEdition(random.randint(1, 3))
                
                # We need a way to represent Playing Card in ShopItem
                # Let's reuse PLANET type temporarily but mark payload as Card
                # Ideally we should add CARD type to ShopItemType
                self.pack_choices.append(ShopItem(ShopItemType.PLANET, 0, card)) # HACK: using PLANET type for now
                
    def select_pack_item(self, index: int):
        """从卡包中选择一张"""
        if index < 0 or index >= len(self.pack_choices):
            return
            
        item = self.pack_choices[index]
        success = False
        
        # Check payload type instead of ShopItemType if we used HACK
        from .card import Card
        if isinstance(item.payload, Card):
            # Standard Pack: Add to deck
            self.deck.cards.append(item.payload)
            success = True
        elif item.type == ShopItemType.JOKER:
            if len(self.jokers) < self.max_jokers:
                self.jokers.append(item.payload)
                item.payload.trigger(None, JokerEvent.ON_JOKER_CREATED)
                success = True
        elif item.type in (ShopItemType.TAROT, ShopItemType.PLANET):
            if len(self.consumables) < self.max_consumables:
                self.consumables.append(item.payload)
                success = True
                
            # 如果是星球包，选择后自动使用 (参考 Balatro 原版机制)
            if success and item.type == ShopItemType.PLANET:
                # 立即使用该星球牌
                # 星球牌不需要目标，直接对 game 生效
                item.payload.use(self, None)
                # 从 consumables 移除刚刚添加的这个星球牌
                self.consumables.pop() 
                # 或者更简单：根本不添加到 consumables，直接使用
                # 但上面的代码已经添加了，所以 pop 掉
                
        
        if success:
            self.state = GameState.SHOP # Return to shop
            self.pack_choices = []
        else:
            # Maybe show message "No room"?
            pass
            
    def skip_pack(self):
        """跳过卡包不选"""
        self.state = GameState.SHOP
        self.pack_choices = []

    
    def reroll_shop(self):
        """重刷商店 (只刷新 Joker 和 Pack 区，保留 Voucher)"""
        if self.money >= self.reroll_cost:
            self.money -= self.reroll_cost
            self.reroll_cost += 1 # 价格递增
            self._init_shop(reset_reroll=False)
            return True
        return False

    def use_consumable(self, index: int, target_card_index: Optional[int] = None):
        """使用消耗品"""
        if index < 0 or index >= len(self.consumables):
            return False
            
        consumable = self.consumables[index]
        target_card = None
        
        # Determine target
        # If in SHOP and using Tarot that needs target:
        # We assume target_card_index refers to DECK index if state is DECK_VIEW or we handle it specially.
        # But UI handles the mapping. 
        # If we are in SHOP, target_card_index should be index in self.deck.cards
        
        if target_card_index is not None:
            if self.state == GameState.PLAYING:
                if 0 <= target_card_index < len(self.hand):
                    target_card = self.hand[target_card_index]
            else: # Shop or other states (Deck View)
                if 0 <= target_card_index < len(self.deck.cards):
                    target_card = self.deck.cards[target_card_index]
            
        if consumable.use(self, target_card):
            # If it's a Tarot that was used from Shop on a deck card, we might need to remove it.
            # But wait, consumables list is in Game.
            # If use() returns True, it means effect succeeded.
            # We should remove it from consumables list.
            
            # Special case: If we are in Deck View selection mode initiated by a consumable,
            # we need to make sure we remove the correct one.
            # The 'index' passed here is the index in self.consumables.
            self.consumables.pop(index)
            return True
        return False
    
    def next_round(self):
        """从商店进入下一轮 (SHOP -> BLIND_SELECT)"""
        # 推进盲注/Ante
        if self.current_blind_type == BlindType.SMALL:
            self.current_blind_type = BlindType.BIG
        elif self.current_blind_type == BlindType.BIG:
            self.current_blind_type = BlindType.BOSS
        elif self.current_blind_type == BlindType.BOSS:
            self.current_blind_type = BlindType.SMALL
            self.ante += 1
            
        self.round += 1
        self.state = GameState.BLIND_SELECT
        # 更新盲注预览
        self.current_blind = Blind(self.current_blind_type, self.ante)

    def debug_create_flush(self):
        """调试功能：在手牌中强制生成一个同花"""
        from .card import Card, Suit, Rank
        # 清空当前手牌
        self.hand = []
        # 生成 5 张黑桃
        for rank in [Rank.TWO, Rank.FIVE, Rank.EIGHT, Rank.TEN, Rank.ACE]:
            self.hand.append(Card(Suit.SPADES, rank))
        # 补满手牌
        self.draw_hand()
        return True

    def game_over(self):
        """游戏失败"""
        self.state = GameState.GAME_OVER

    def _init_hand_levels(self) -> Dict[HandType, Dict[str, Any]]:
        """初始化牌型等级"""
        levels = {}
        for hand_type, (chips, mult) in HandEvaluator.HAND_SCORES.items():
            levels[hand_type] = {
                "level": 1,
                "chips": chips,
                "mult": mult
            }
        return levels

    def upgrade_hand(self, hand_type: HandType, chips_up: int = 15, mult_up: int = 1):
        """升级指定牌型"""
        if hand_type in self.hand_levels:
            self.hand_levels[hand_type]["level"] += 1
            self.hand_levels[hand_type]["chips"] += chips_up
            self.hand_levels[hand_type]["mult"] += mult_up
            return True
        return False

    def start_game(self, deck_type: DeckType = DeckType.RED):
        """开始新游戏"""
        self.state = GameState.BLIND_SELECT
        self.deck_type = deck_type
        self.deck = Deck(deck_type)
        self.money = 4  # 初始资金
        self.ante = 1
        self.round = 0
        self.jokers = []
        self.consumables = []
        self.hand_levels = self._init_hand_levels()
        self.current_blind_type = BlindType.SMALL
        
        # Apply Deck Effects
        self.max_hands = 4
        self.max_discards = 3
        
        if deck_type == DeckType.RED:
            self.max_discards += 1 # Red Deck: +1 Discard
        elif deck_type == DeckType.BLUE:
            self.max_hands += 1 # Blue Deck: +1 Hand
        elif deck_type == DeckType.YELLOW:
            self.money += 10 # Yellow Deck: Start with extra $10
            
        # 预先加载第一个盲注信息
        self.current_blind = Blind(self.current_blind_type, self.ante)

    def skip_blind(self):
        """跳过当前盲注"""
        if self.current_blind_type == BlindType.BOSS:
            return # Boss Blind 不能跳过
            
        # 给予 Tag 奖励 (简化实现：直接给钱或随机效果)
        import random
        tag_effect = random.choice(["FREE_SHOP", "MONEY", "HAND_LEVEL"])
        
        if tag_effect == "MONEY":
            self.money += 10 # Investment Tag
        elif tag_effect == "HAND_LEVEL":
            # Upgrade a random hand
            hand = random.choice(list(self.hand_levels.keys()))
            self.upgrade_hand(hand, 30, 3)
        elif tag_effect == "FREE_SHOP":
            # This would require a 'free_shop' flag in state
            self.money += 15 # Simplified as money for now
            
        self.state = GameState.SHOP
        self._init_shop()

    def start_round(self):
        """选择当前盲注并开始回合 (从 BLIND_SELECT -> PLAYING)"""
        # 重新生成盲注对象以确保数据最新
        self.current_blind = Blind(self.current_blind_type, self.ante)
        self.target_score = self.current_blind.score_requirement
        self.current_score = 0
        self.hands_remaining = self.max_hands
        self.discards_remaining = self.max_discards
        self.state = GameState.PLAYING
        
        # 触发 Joker: ON_BLIND_SELECTED
        self._trigger_jokers(None, JokerEvent.ON_BLIND_SELECTED)
        
        # 洗牌发牌
        self.deck.shuffle()
        self.hand = []
        self.draw_hand()

    def draw_hand(self):
        """补满手牌"""
        while len(self.hand) < self.max_hand_size and len(self.deck) > 0:
            card = self.deck.draw()
            if card:
                self.hand.append(card)

    def calculate_potential_score(self, card_indices: List[int]) -> Dict[str, Any]:
        """计算选中牌的潜在得分（包含详细 Breakdown）"""
        if not card_indices:
            return {
                "base_chips": 0, "base_mult": 0,
                "card_chips": 0, "card_mult": 0, "card_xmult": 1.0,
                "joker_chips": 0, "joker_mult": 0, "joker_xmult": 1.0,
                "total_chips": 0, "total_mult": 0, "final_score": 0,
                "hand_name": "None"
            }
            
        selected_cards = [self.hand[i] for i in sorted(card_indices)]
        
        # 1. 识别牌型
        hand_type = HandEvaluator.evaluate(selected_cards)
        
        # 2. 计算基础得分
        hand_level = self.hand_levels.get(hand_type, {"chips": 0, "mult": 0})
        base_chips = hand_level["chips"]
        base_mult = hand_level["mult"]
        
        # Breakdown vars
        card_chips_total = 0
        card_mult_total = 0
        card_xmult_total = 1.0
        
        joker_chips_total = 0
        joker_mult_total = 0
        joker_xmult_total = 1.0
        
        # Temp totals
        chips = base_chips
        mult = base_mult
        
        # 3. 计算 Joker 效果 (Balatro 的核心计分链)
        
        # A. 遍历每一张计分的卡牌
        for card in selected_cards:
            # 1. 基础卡牌加成 (Enhancements & Editions)
            c_chips = card.get_value() + card.get_chip_bonus()
            c_mult = card.get_mult_bonus()
            c_xmult = card.get_xmult_bonus()
            
            card_chips_total += c_chips
            card_mult_total += c_mult
            if c_xmult > 1.0:
                 card_xmult_total *= c_xmult
            
            chips += c_chips
            mult += c_mult
            mult = int(mult * c_xmult)
            
            # 2. 触发 Joker: ON_CARD_SCORED
            effects = self._get_joker_effects(card, JokerEvent.ON_CARD_SCORED)
            for eff in effects:
                joker_chips_total += eff.chips
                joker_mult_total += eff.mult
                if eff.xmult > 0:
                    joker_xmult_total *= eff.xmult
                
                chips += eff.chips
                mult += eff.mult
                if eff.xmult > 0:
                    mult = int(mult * eff.xmult)
        
        # A2. 遍历手牌中未打出的牌 (触发钢卡等 Held in hand 效果)
        remaining_hand = [c for i, c in enumerate(self.hand) if i not in card_indices]
        for card in remaining_hand:
            # 钢卡效果
            if card.enhancement == CardType.STEEL:
                card_xmult_total *= 1.5
                mult = int(mult * 1.5)
            
            # 触发 Joker: ON_CARD_HELD
            effects = self._get_joker_effects(card, JokerEvent.ON_CARD_HELD)
            for eff in effects:
                joker_chips_total += eff.chips
                joker_mult_total += eff.mult
                if eff.xmult > 0:
                    joker_xmult_total *= eff.xmult
                    
                chips += eff.chips
                mult += eff.mult
                if eff.xmult > 0:
                    mult = int(mult * eff.xmult)
        
        # B. 触发独立 Joker 效果 (INDEPENDENT)
        effects = self._get_joker_effects(None, JokerEvent.INDEPENDENT, {
            'hand_type': hand_type,
            'played_cards': selected_cards,
            'money': self.money,
            'deck_size': len(self.deck),
            'jokers': self.jokers,
            'max_jokers': self.max_jokers
        })
        for eff in effects:
            joker_chips_total += eff.chips
            joker_mult_total += eff.mult
            if eff.xmult > 0:
                joker_xmult_total *= eff.xmult
                
            chips += eff.chips
            mult += eff.mult
            if eff.xmult > 0:
                mult = int(mult * eff.xmult)
        
        final_score = chips * mult
        
        return {
            "base_chips": base_chips, "base_mult": base_mult,
            "card_chips": card_chips_total, "card_mult": card_mult_total, "card_xmult": card_xmult_total,
            "joker_chips": joker_chips_total, "joker_mult": joker_mult_total, "joker_xmult": joker_xmult_total,
            "total_chips": chips, "total_mult": mult, "final_score": final_score,
            "hand_name": hand_type.name
        }

    def play_hand(self, card_indices: List[int]):
        """出牌逻辑"""
        if self.hands_remaining <= 0:
            return

        selected_cards = [self.hand[i] for i in sorted(card_indices)]
        
        # 1. 识别牌型
        hand_type = HandEvaluator.evaluate(selected_cards)
        
        # 触发 Joker: ON_HAND_PLAYED
        self._trigger_jokers(None, JokerEvent.ON_HAND_PLAYED, {
            'hand_type': hand_type,
            'played_cards': selected_cards
        })

        # 2. 计算基础得分
        # 从动态等级系统获取基础分
        hand_level = self.hand_levels.get(hand_type, {"chips": 0, "mult": 0})
        base_chips = hand_level["chips"]
        base_mult = hand_level["mult"]
        
        # 计算卡牌筹码
        card_chips = sum(card.get_value() for card in selected_cards)
        
        # 总筹码 = 基础筹码 + 卡牌筹码
        chips = base_chips + card_chips
        mult = base_mult
        
        # 3. 计算 Joker 效果 (Balatro 的核心计分链)
        
        # A. 遍历每一张计分的卡牌
        for card in selected_cards:
            # 1. 基础卡牌加成 (Enhancements & Editions)
            chips += card.get_chip_bonus()
            mult += card.get_mult_bonus()
            mult = int(mult * card.get_xmult_bonus())
            
            # 2. 触发 Joker: ON_CARD_SCORED
            effects = self._get_joker_effects(card, JokerEvent.ON_CARD_SCORED)
            for eff in effects:
                chips += eff.chips
                mult += eff.mult
                if eff.xmult > 0:
                    mult = int(mult * eff.xmult)
        
        # A2. 遍历手牌中未打出的牌 (触发钢卡等 Held in hand 效果)
        # 注意：在 Balatro 中，Held in Hand 效果通常是在所有计分卡结算完之后触发
        for card in self.hand:
            # 钢卡效果: 手持时 x1.5 Mult
            if card.enhancement == CardType.STEEL:
                mult = int(mult * 1.5)
            
            # 触发 Joker: ON_CARD_HELD
            effects = self._get_joker_effects(card, JokerEvent.ON_CARD_HELD)
            for eff in effects:
                chips += eff.chips
                mult += eff.mult
                if eff.xmult > 0:
                    mult = int(mult * eff.xmult)
        
        # B. 触发独立 Joker 效果 (INDEPENDENT) - 大多数加倍率的 Joker 在这里
        # 注意：这里需要传入当前上下文，包括手牌类型、打出的牌、金钱等
        effects = self._get_joker_effects(None, JokerEvent.INDEPENDENT, {
            'hand_type': hand_type,
            'played_cards': selected_cards,
            'money': self.money,
            'deck_size': len(self.deck),
            'jokers': self.jokers,
            'max_jokers': self.max_jokers
        })
        for eff in effects:
            chips += eff.chips
            mult += eff.mult
            if eff.xmult > 0:
                mult = int(mult * eff.xmult)
        
        final_hand_score = chips * mult
        self.current_score += final_hand_score
        self.hands_remaining -= 1
        
        # 4. 从手牌移除
        for card in selected_cards:
            self.hand.remove(card)
            
        # 5. 检查回合结束
        if self.current_score >= self.target_score:
            self.win_round()
        elif self.hands_remaining == 0:
            self.game_over()
        else:
            self.draw_hand()

    def _get_joker_effects(self, card: Optional[Card], event: JokerEvent, context: Dict = None) -> List[JokerEffect]:
        """获取所有 Joker 的触发效果"""
        results = []
        # 按顺序触发，这在 Balatro 中很重要 (特别是 XMult)
        for joker in self.jokers:
            eff = joker.trigger(card, event, context)
            if eff:
                results.append(eff)
        return results

    def _trigger_jokers(self, card: Optional[Card], event: JokerEvent, context: Dict = None):
        """触发 Joker 效果并处理副作用 (如过期)"""
        expired_jokers = []
        for joker in self.jokers:
            eff = joker.trigger(card, event, context)
            if eff and eff.expire:
                expired_jokers.append(joker)
        
        for j in expired_jokers:
            if j in self.jokers:
                self.jokers.remove(j)

    def discard_hand(self, card_indices: List[int]):
        """弃牌逻辑"""
        if self.discards_remaining <= 0:
            return

        selected_cards = [self.hand[i] for i in sorted(card_indices)]
        
        # 触发 Joker: ON_HAND_DISCARDED
        self._trigger_jokers(None, JokerEvent.ON_HAND_DISCARDED, {'discarded_cards': selected_cards})
        
        for card in selected_cards:
            self.hand.remove(card)
            
        self.discards_remaining -= 1
        self.draw_hand()

    def win_round(self):
        """回合胜利 (PLAYING -> ROUND_END)"""
        self.state = GameState.ROUND_END
        
        # 触发 Joker: ON_ROUND_END
        self._trigger_jokers(None, JokerEvent.ON_ROUND_END)
        
        # 计算奖励
        blind_reward = self.current_blind.reward
        hands_reward = self.hands_remaining # $1 per remaining hand
        
        # 利息计算: 每 $5 获得 $1，上限 $5 (默认)
        # 允许通过 Joker 或 Voucher 修改上限 (暂未实现修改接口，先硬编码逻辑)
        interest_cap = self.max_interest
        self.interest = min((self.money // 5) * self.interest_per_5, interest_cap)
        
        self.round_reward = blind_reward + hands_reward + self.interest
        self.money += self.round_reward

    def finish_round(self):
        """结束回合结算，进入商店 (ROUND_END -> SHOP)"""
        # 如果是 Boss Blind 且通过了 Ante 8，则胜利
        if self.current_blind_type == BlindType.BOSS and self.ante >= self.max_ante:
            self.state = GameState.WIN
        else:
            self.state = GameState.SHOP
            self._init_shop()
