import msvcrt
import os
import time
from typing import List, Optional, Tuple

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich import box
from rich.style import Style

from .game import Game
from .card import Card, Suit, Rank
from .enums import GameState, BlindType
from .blind import Blind
from .hand_analysis import HandEvaluator, HandType

class TUI:
    def __init__(self, game: Game):
        self.game = game
        self.console = Console()
        self.selected_indices: set[int] = set()
        self.cursor_index = 0
        self.message = ""
        
        # UI State
        self.focus_area = "hand"  # "hand" or "actions"
        self.action_index = 0     # 0: Play, 1: Discard
        
    def run(self):
        """主循环"""
        self.game.start_game()
        
        # refresh_per_second 不能为 None 或 0，即使 auto_refresh=False
        # 我们设置为一个较低的值即可，因为我们主要靠手动刷新
        with Live(self.render_layout(), refresh_per_second=4, screen=True, auto_refresh=False) as live:
            self.live = live # 保存引用以便手动刷新
            
            while True:
                # 只有在状态改变或用户输入后才刷新
                # 但由于我们这里是简单的轮询，我们先限制帧率，并只在必要时 update
                
                # 强制刷新一次以显示初始状态
                live.update(self.render_layout(), refresh=True)
                
                if self.game.state == GameState.GAME_OVER or self.game.state == GameState.WIN:
                    if msvcrt.kbhit():
                         break
                    time.sleep(0.05)
                    continue

                input_processed = False
                if self.game.state == GameState.BLIND_SELECT:
                    input_processed = self.handle_blind_select_input()
                elif self.game.state == GameState.PLAYING:
                    input_processed = self.handle_playing_input()
                elif self.game.state == GameState.ROUND_END:
                    input_processed = self.handle_round_end_input()
                elif self.game.state == GameState.SHOP:
                    input_processed = self.handle_shop_input()
                
                # 只有当处理了输入时，才立即刷新，否则等待
                if not input_processed:
                    time.sleep(0.05)
                # 注意：Rich Live 的 update 会在下一次 refresh 时生效
                # 或者我们可以显式调用 refresh() 如果 auto_refresh=False


    def handle_blind_select_input(self) -> bool:
        # Press Enter to start round, Q to quit
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\r': # Enter
                self.game.start_round()
                return True
            elif key == b'q':
                exit()
        return False

    def handle_round_end_input(self) -> bool:
        # Press Enter to go to Shop
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\r':
                self.game.finish_round()
                return True
        return False

    def handle_shop_input(self) -> bool:
        # Press N for Next Round
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'n':
                self.game.next_round()
                return True
        return False

    def handle_playing_input(self) -> bool:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            processed = True
            
            # Handle special keys (arrows)
            if key == b'\xe0':
                key = msvcrt.getch()
                if key == b'K': # Left
                    if self.focus_area == "hand":
                        self.cursor_index = max(0, self.cursor_index - 1)
                    else:
                        self.action_index = max(0, self.action_index - 1)
                elif key == b'M': # Right
                    if self.focus_area == "hand":
                        self.cursor_index = min(len(self.game.hand) - 1, self.cursor_index + 1)
                    else:
                        self.action_index = min(1, self.action_index + 1)
                elif key == b'H': # Up
                    if self.focus_area == "actions":
                        self.focus_area = "hand"
                        self.cursor_index = min(self.cursor_index, len(self.game.hand) - 1)
                elif key == b'P': # Down
                    if self.focus_area == "hand":
                        self.focus_area = "actions"
                else:
                    processed = False
            
            elif key == b' ': # Space to toggle selection
                if self.focus_area == "hand":
                    if self.cursor_index in self.selected_indices:
                        self.selected_indices.remove(self.cursor_index)
                    else:
                        if len(self.selected_indices) < 5:
                            self.selected_indices.add(self.cursor_index)
                        else:
                            self.message = "最多只能选择5张牌！"
                else:
                    processed = False

            elif key == b'\r': # Enter to confirm
                if self.focus_area == "actions":
                    if self.action_index == 0: # Play
                        self.play_hand()
                    else: # Discard
                        self.discard_hand()
                elif self.focus_area == "hand":
                    if self.cursor_index in self.selected_indices:
                        self.selected_indices.remove(self.cursor_index)
                    else:
                        if len(self.selected_indices) < 5:
                            self.selected_indices.add(self.cursor_index)
                else:
                    processed = False
            
            elif key == b'q':
                exit()
            else:
                processed = False
            
            return processed
        return False

    def play_hand(self):
        if not self.selected_indices:
            self.message = "请先选择牌！"
            return
            
        if self.game.hands_remaining <= 0:
            self.message = "没有出牌次数了！"
            return

        indices = list(self.selected_indices)
        
        # Calculate score for display message before cards are removed
        selected_cards = [self.game.hand[i] for i in indices]
        hand_type = HandEvaluator.evaluate(selected_cards)
        score, chips, mult = HandEvaluator.calculate_score(selected_cards)
        
        self.game.play_hand(indices)
        self.selected_indices.clear()
        self.cursor_index = 0
        self.message = f"打出 {hand_type.name}! 得分: {score}"

    def discard_hand(self):
        if not self.selected_indices:
            self.message = "请先选择牌！"
            return
            
        if self.game.discards_remaining <= 0:
            self.message = "没有弃牌次数了！"
            return
            
        self.game.discard_hand(list(self.selected_indices))
        self.selected_indices.clear()
        self.cursor_index = 0
        self.message = "弃牌成功"

    def render_layout(self) -> Layout:
        layout = Layout()
        
        if self.game.state == GameState.BLIND_SELECT:
            layout.update(self.render_blind_select())
        elif self.game.state == GameState.PLAYING:
            layout.split_column(
                Layout(self.render_header(), size=3),
                Layout(self.render_score_area(), size=5),
                Layout(self.render_game_area(), ratio=1),
                Layout(self.render_controls(), size=3)
            )
        elif self.game.state == GameState.ROUND_END:
            layout.update(self.render_round_end())
        elif self.game.state == GameState.SHOP:
            layout.update(self.render_shop())
        elif self.game.state == GameState.GAME_OVER:
            layout.update(Panel("GAME OVER", style="bold red"))
        elif self.game.state == GameState.WIN:
            layout.update(Panel("YOU WIN!", style="bold green"))
            
        return layout

    def render_blind_select(self) -> Panel:
        blind = self.game.current_blind
        
        table = Table(title=f"Ante {self.game.ante}", box=box.ROUNDED)
        table.add_column("Current Blind", justify="center", style="cyan")
        table.add_column("Score Target", justify="center", style="bold red")
        table.add_column("Reward", justify="center", style="green")
        
        table.add_row(blind.type.name, str(blind.score_requirement), f"${blind.reward}")
        
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row(table)
        content.add_row("")
        content.add_row("[blink bold]Press ENTER to Play Round[/]")
        
        return Panel(content, title="Blind Selection")

    def render_round_end(self) -> Panel:
        table = Table(title="Round Victory!", box=box.DOUBLE)
        table.add_column("Item", justify="left")
        table.add_column("Value", justify="right", style="green")
        
        table.add_row("Blind Reward", f"${self.game.current_blind.reward}")
        table.add_row("Hands Left", f"${self.game.hands_remaining}")
        table.add_row("Interest", f"${self.game.interest}")
        table.add_row("", "")
        table.add_row("Total Earned", f"${self.game.round_reward}", style="bold green")
        table.add_row("Current Money", f"${self.game.money}", style="bold yellow")
        
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row(table)
        content.add_row("")
        content.add_row("Press ENTER to continue")
        
        return Panel(content, title="Cash Out")

    def render_shop(self) -> Panel:
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row(Text("SHOP", style="bold yellow"))
        content.add_row("")
        content.add_row("Coming Soon...")
        content.add_row("")
        content.add_row("Press N for Next Round")
        
        return Panel(content, title="Shop")

    def render_header(self) -> Table:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(
            f"Ante: {self.game.ante}  Round: {self.game.round}",
            f"Money: ${self.game.money}"
        )
        return grid

    def render_score_area(self) -> Panel:
        # Calculate potential score of selected cards
        potential_text = ""
        if self.selected_indices:
            selected_cards = [self.game.hand[i] for i in self.selected_indices if i < len(self.game.hand)]
            if selected_cards:
                hand_type = HandEvaluator.evaluate(selected_cards)
                score, chips, mult = HandEvaluator.calculate_score(selected_cards)
                potential_text = f" | 选中: {hand_type.name} ({chips} x {mult} = {score})"

        content = Text()
        content.append(f"目标分数: {self.game.target_score}\n", style="bold")
        content.append(f"当前分数: {self.game.current_score}", style="blue")
        content.append(potential_text, style="dim")
        
        return Panel(content, title="计分板", border_style="blue")

    def render_game_area(self) -> Panel:
        # Render cards
        hand_table = Table.grid(padding=1)
        
        row_cards = []
        for i, card in enumerate(self.game.hand):
            style = "white"
            if card.suit in (Suit.HEARTS, Suit.DIAMONDS):
                style = "red"
            
            # Selection & Cursor logic
            is_selected = i in self.selected_indices
            is_cursor = (i == self.cursor_index) and (self.focus_area == "hand")
            
            card_text = self.get_card_art(card)
            
            border_style = style
            if is_cursor:
                border_style = "bold yellow"
            elif is_selected:
                border_style = "bold green"
                
            # If selected, move it up visually (handled by padding/margin in a real TUI, 
            # here we just change border style or color)
            
            box_type = box.DOUBLE if is_selected else box.ROUNDED
            if is_cursor:
                box_type = box.HEAVY
                
            panel = Panel(
                card_text, 
                border_style=border_style, 
                box=box_type,
                width=8,
                height=3
            )
            row_cards.append(panel)
            
        hand_table.add_row(*row_cards)
        
        # Center the hand
        centered_table = Table.grid(expand=True)
        centered_table.add_column(justify="center")
        centered_table.add_row(hand_table)
        
        return Panel(centered_table, title="手牌区 (Space:选中/取消, 方向键:移动)", border_style="white")

    def render_controls(self) -> Table:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)
        
        play_style = "white"
        discard_style = "white"
        
        if self.focus_area == "actions":
            if self.action_index == 0:
                play_style = "reverse bold green"
            else:
                discard_style = "reverse bold red"
                
        grid.add_row(
            Text(f"出牌 ({self.game.hands_remaining})", style=play_style),
            Text(f"弃牌 ({self.game.discards_remaining})", style=discard_style)
        )
        
        # Add message
        msg_grid = Table.grid(expand=True)
        msg_grid.add_row(grid)
        msg_grid.add_row(Text(self.message, justify="center", style="yellow"))
        
        return msg_grid

    def get_card_art(self, card: Card) -> Text:
        rank_str = card.rank.name
        # Simplify rank names
        rank_map = {
            "TWO": "2", "THREE": "3", "FOUR": "4", "FIVE": "5",
            "SIX": "6", "SEVEN": "7", "EIGHT": "8", "NINE": "9",
            "TEN": "10", "JACK": "J", "QUEEN": "Q", "KING": "K", "ACE": "A"
        }
        r = rank_map.get(rank_str, "?")
        
        suit_map = {
            "HEARTS": "♥", "DIAMONDS": "♦", 
            "CLUBS": "♣", "SPADES": "♠"
        }
        s = suit_map.get(card.suit.name, "?")
        
        color = "red" if card.suit in (Suit.HEARTS, Suit.DIAMONDS) else "white"
        
        # Pure text representation: "♥ A" or "♣ 10"
        text = Text()
        text.append(f"{s} {r}", style=color)
        
        return text
