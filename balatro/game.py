from typing import List, Optional
from .card import Card
from .deck import Deck
from .enums import GameState, BlindType
from .blind import Blind
from .hand_analysis import HandEvaluator, HandType

class Game:
    def __init__(self):
        # 基础状态
        self.state = GameState.MAIN_MENU
        self.deck = Deck()
        self.hand: List[Card] = []
        self.discards_remaining = 0
        self.hands_remaining = 0
        self.money = 0
        self.ante = 1
        self.round = 0
        self.current_blind_type = BlindType.SMALL
        self.current_blind: Optional[Blind] = None
        self.current_score = 0
        self.target_score = 0
        
        # 奖励信息 (Round End 使用)
        self.round_reward = 0
        self.interest = 0
        
        # 游戏配置
        self.max_hand_size = 8
        self.max_hands = 4
        self.max_discards = 4
        self.max_ante = 8
        self.max_interest = 5
        self.interest_per_5 = 1

    def start_game(self):
        """开始新游戏"""
        self.state = GameState.BLIND_SELECT
        self.deck = Deck()
        self.money = 4  # 初始资金
        self.ante = 1
        self.round = 0
        self.current_blind_type = BlindType.SMALL
        # 预先加载第一个盲注信息
        self.current_blind = Blind(self.current_blind_type, self.ante)

    def start_round(self):
        """选择当前盲注并开始回合 (从 BLIND_SELECT -> PLAYING)"""
        # 重新生成盲注对象以确保数据最新
        self.current_blind = Blind(self.current_blind_type, self.ante)
        self.target_score = self.current_blind.score_requirement
        self.current_score = 0
        self.hands_remaining = self.max_hands
        self.discards_remaining = self.max_discards
        self.state = GameState.PLAYING
        
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

    def play_hand(self, card_indices: List[int]):
        """出牌逻辑"""
        if self.hands_remaining <= 0:
            return

        selected_cards = [self.hand[i] for i in sorted(card_indices)]
        
        # 1. 验证牌型并计分
        score, chips, mult = HandEvaluator.calculate_score(selected_cards)
        self.current_score += score
        self.hands_remaining -= 1
        
        # 2. 从手牌移除
        for card in selected_cards:
            self.hand.remove(card)
            
        # 3. 检查回合结束
        if self.current_score >= self.target_score:
            self.win_round()
        elif self.hands_remaining == 0:
            self.game_over()
        else:
            self.draw_hand()

    def discard_hand(self, card_indices: List[int]):
        """弃牌逻辑"""
        if self.discards_remaining <= 0:
            return

        selected_cards = [self.hand[i] for i in sorted(card_indices)]
        
        for card in selected_cards:
            self.hand.remove(card)
            
        self.discards_remaining -= 1
        self.draw_hand()

    def win_round(self):
        """回合胜利 (PLAYING -> ROUND_END)"""
        self.state = GameState.ROUND_END
        
        # 计算奖励
        blind_reward = self.current_blind.reward
        hands_reward = self.hands_remaining # $1 per remaining hand
        
        # 利息计算: 每 $5 获得 $1，上限 $5 (默认)
        self.interest = min((self.money // 5) * self.interest_per_5, self.max_interest)
        
        self.round_reward = blind_reward + hands_reward + self.interest
        self.money += self.round_reward

    def finish_round(self):
        """结束回合结算，进入商店 (ROUND_END -> SHOP)"""
        # 如果是 Boss Blind 且通过了 Ante 8，则胜利
        if self.current_blind_type == BlindType.BOSS and self.ante >= self.max_ante:
            self.state = GameState.WIN
        else:
            self.state = GameState.SHOP

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

    def game_over(self):
        """游戏失败"""
        self.state = GameState.GAME_OVER
