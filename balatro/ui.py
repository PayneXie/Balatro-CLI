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
from .joker import Joker
from .consumable import Consumable
from .shop import ShopItem, ShopItemType

class TUI:
    def __init__(self, game: Game):
        self.game = game
        self.console = Console()
        self.selected_indices: set[int] = set()
        self.cursor_index = 0
        self.message = ""
        
        # UI State
        self.focus_area = "hand"  # "hand", "actions", "consumables", "jokers"
        self.action_index = 0     # 0: Play, 1: Discard
        self.consumable_index = 0
        self.joker_index = 0
        
        # Shop State
        self.shop_cursor_index = 0
        self.shop_zone_index = 0  # 0: Cards, 1: Packs, 2: Voucher
        
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
        # Press Enter to start round, S to skip, Q to quit
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\r': # Enter
                self.game.start_round()
                return True
            elif key == b's': # Skip
                self.game.skip_blind()
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
        # Shop Controls:
        # Arrows: Move cursor
        # Enter: Buy item
        # R: Reroll
        # N: Next Round
        
        if msvcrt.kbhit():
            key = msvcrt.getch()
            processed = True
            
            if key == b'\xe0': # Arrows
                key = msvcrt.getch()
                if key == b'K': # Left
                    self.shop_cursor_index = max(0, self.shop_cursor_index - 1)
                elif key == b'M': # Right
                    # Limit based on current zone
                    max_idx = 0
                    if self.shop_zone_index == 0: max_idx = len(self.game.joker_slots) - 1
                    elif self.shop_zone_index == 1: max_idx = len(self.game.pack_slots) - 1
                    elif self.shop_zone_index == 2: max_idx = 0
                    self.shop_cursor_index = min(max_idx, self.shop_cursor_index + 1)
                elif key == b'H': # Up
                    if self.shop_zone_index > 0:
                        self.shop_zone_index -= 1
                        self.shop_cursor_index = 0
                elif key == b'P': # Down
                    if self.shop_zone_index < 2:
                        self.shop_zone_index += 1
                        self.shop_cursor_index = 0
                else:
                    processed = False
                    
            elif key == b'\r': # Enter -> Buy
                self.game.buy_item(self.shop_zone_index, self.shop_cursor_index)
                # Adjust cursor if items reduced
                max_idx = 0
                if self.shop_zone_index == 0: max_idx = len(self.game.joker_slots) - 1
                elif self.shop_zone_index == 1: max_idx = len(self.game.pack_slots) - 1
                elif self.shop_zone_index == 2: max_idx = 0 if self.game.voucher_slot else -1
                self.shop_cursor_index = max(0, min(self.shop_cursor_index, max_idx))
                        
            elif key == b'r': # Reroll
                if self.game.reroll_shop():
                    self.shop_cursor_index = 0
                    self.shop_zone_index = 0
                else:
                    self.message = "Not enough money to reroll!"
                    
            elif key == b'n': # Next Round
                self.game.next_round()
                
            else:
                processed = False
                
            return processed
        return False

    def handle_playing_input(self) -> bool:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            processed = True
            
            # Handle special keys (arrows)
            if key == b'\xe0':
                key = msvcrt.getch()
                if key == b'H': # Up
                    if self.focus_area == "consumables":
                        self.focus_area = "actions"
                    elif self.focus_area == "actions":
                        self.focus_area = "hand"
                        self.cursor_index = min(self.cursor_index, len(self.game.hand) - 1)
                    elif self.focus_area == "hand" and self.game.jokers:
                        self.focus_area = "jokers"
                        self.joker_index = 0
                elif key == b'P': # Down
                    if self.focus_area == "jokers":
                        self.focus_area = "hand"
                    elif self.focus_area == "hand":
                        self.focus_area = "actions"
                    elif self.focus_area == "actions" and self.game.consumables:
                        self.focus_area = "consumables"
                        self.consumable_index = 0
                elif key == b'K': # Left
                    if self.focus_area == "hand":
                        self.cursor_index = max(0, self.cursor_index - 1)
                    elif self.focus_area == "actions":
                        self.action_index = max(0, self.action_index - 1)
                    elif self.focus_area == "jokers":
                        self.joker_index = max(0, self.joker_index - 1)
                elif key == b'M': # Right
                    if self.focus_area == "hand":
                        self.cursor_index = min(len(self.game.hand) - 1, self.cursor_index + 1)
                    elif self.focus_area == "actions":
                        self.action_index = min(1, self.action_index + 1)
                    elif self.focus_area == "jokers":
                        self.joker_index = min(len(self.game.jokers) - 1, self.joker_index + 1)
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
                elif self.focus_area == "consumables":
                    self.use_consumable()
                elif self.focus_area == "jokers":
                    if self.game.jokers and self.joker_index < len(self.game.jokers):
                        joker = self.game.jokers[self.joker_index]
                        self.message = f"{joker.name_cn}: {joker.desc}"
                else:
                    processed = False
            
            elif key == b'q':
                exit()
            
            # Debug Keys
            elif key == b'F': # Shift+F: Force Flush
                self.game.debug_create_flush()
                self.message = "Debug: 生成同花!"
                self.selected_indices.clear()
                self.cursor_index = 0
            
            else:
                processed = False
            
            return processed
        return False

    def use_consumable(self):
        if not self.game.consumables:
            return
            
        # Determine target card
        target_index = None
        # 如果选中了牌，且只能选一张，则作为目标
        if len(self.selected_indices) == 1:
            target_index = list(self.selected_indices)[0]
        elif len(self.selected_indices) == 0 and self.cursor_index < len(self.game.hand):
             # 如果没选中，用光标下的牌（某些塔罗牌需要）
             target_index = self.cursor_index
             
        if self.game.use_consumable(self.consumable_index, target_index):
            self.message = "消耗品使用成功！"
            # Adjust index if list shrunk
            if self.consumable_index >= len(self.game.consumables):
                self.consumable_index = max(0, len(self.game.consumables) - 1)
            if not self.game.consumables:
                self.focus_area = "actions"
        else:
            self.message = "无法使用该消耗品（可能需要选中一张牌）"

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
                Layout(self.render_jokers(), size=4),
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

    def render_jokers(self) -> Panel:
        if not self.game.jokers:
            return Panel(Text("No Jokers", style="dim", justify="center"), title="Jokers", height=3)
            
        joker_row = []
        for i, j in enumerate(self.game.jokers):
            style = "blue"
            box_type = box.ROUNDED
            if self.focus_area == "jokers" and i == self.joker_index:
                style = "bold blue"
                box_type = box.HEAVY
            
            panel = Panel(
                Text(j.name_cn, justify="center"),
                border_style=style,
                box=box_type,
                width=16,
                height=3
            )
            joker_row.append(panel)
            
        grid = Table.grid(padding=1)
        grid.add_row(*joker_row)
        
        return Panel(grid, title="Jokers (Up to select, Enter for info)", title_align="left")

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
        
        if self.game.current_blind_type != BlindType.BOSS:
            content.add_row("[blink bold]Press ENTER to Play Round[/] | [bold yellow]Press S to SKIP[/]")
        else:
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
        # Shop Header
        header = Table.grid(expand=True)
        header.add_column(justify="left")
        header.add_column(justify="right")
        header.add_row(
            Text(f"SHOP - Reroll: ${self.game.reroll_cost}", style="bold yellow"),
            Text(f"Money: ${self.game.money}", style="bold green")
        )
        
        # Helper to create item panels
        def create_item_panel(index, item, zone_idx):
            border_style = "white"
            box_type = box.ROUNDED
            
            if zone_idx == self.shop_zone_index and index == self.shop_cursor_index:
                border_style = "bold yellow"
                box_type = box.HEAVY
            
            title = item.name_cn
            desc = item.desc
            if not desc and item.type == ShopItemType.VOUCHER:
                 desc = "优惠券"
            
            cost = f"${item.price}"
            
            # Create item panel
            item_content = Text()
            item_content.append(f"{title}\n", style="bold")
            item_content.append(f"{desc}\n", style="dim")
            item_content.append(f"\n{cost}", style="green")
            
            return Panel(
                item_content,
                border_style=border_style,
                box=box_type,
                width=20,
                height=6
            )

        # 1. Card Zone (Jokers/Consumables)
        card_zone_title = Text("Cards (Jokers/Consumables)", style="bold cyan")
        if self.shop_zone_index == 0: card_zone_title.style = "reverse bold cyan"
        
        card_zone_row = []
        current_idx = 0
        
        for item in self.game.joker_slots:
            card_zone_row.append(create_item_panel(current_idx, item, 0))
            current_idx += 1
            
        if not card_zone_row:
            card_zone_row.append(Text("Empty", style="dim"))

        # 2. Pack Zone
        pack_zone_title = Text("Packs", style="bold blue")
        if self.shop_zone_index == 1: pack_zone_title.style = "reverse bold blue"
        
        pack_zone_row = []
        current_idx = 0
        
        for item in self.game.pack_slots:
            pack_zone_row.append(create_item_panel(current_idx, item, 1))
            current_idx += 1
            
        if not pack_zone_row:
            pack_zone_row.append(Text("Empty", style="dim"))

        # 3. Voucher Zone
        voucher_zone_title = Text("Voucher", style="bold magenta")
        if self.shop_zone_index == 2: voucher_zone_title.style = "reverse bold magenta"
        
        voucher_zone_row = []
        
        if self.game.voucher_slot:
            voucher_zone_row.append(create_item_panel(0, self.game.voucher_slot, 2))
        else:
            voucher_zone_row.append(Text("Sold Out", style="dim"))

        
        # Owned Jokers & Consumables
        inventory_table = Table(title="Inventory", box=box.SIMPLE, show_header=True)
        inventory_table.add_column("Jokers", style="bold blue")
        inventory_table.add_column("Consumables", style="bold magenta")
        
        jokers_str = "\n".join([f"- {j.name_cn}" for j in self.game.jokers]) if self.game.jokers else "None"
        consumables_str = "\n".join([f"- {c.name_cn}" for c in self.game.consumables]) if self.game.consumables else "None"
        
        inventory_table.add_row(jokers_str, consumables_str)

        # Layout
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row(header)
        content.add_row("")
        
        # Zone 1
        content.add_row(card_zone_title)
        if card_zone_row and isinstance(card_zone_row[0], Panel):
             grid1 = Table.grid(padding=1)
             grid1.add_row(*card_zone_row)
             content.add_row(grid1)
        else:
             content.add_row(*card_zone_row)
        content.add_row("")
        
        # Zone 2
        content.add_row(pack_zone_title)
        if pack_zone_row and isinstance(pack_zone_row[0], Panel):
             grid2 = Table.grid(padding=1)
             grid2.add_row(*pack_zone_row)
             content.add_row(grid2)
        else:
             content.add_row(*pack_zone_row)
        content.add_row("")

        # Zone 3
        content.add_row(voucher_zone_title)
        if voucher_zone_row and isinstance(voucher_zone_row[0], Panel):
             grid3 = Table.grid(padding=1)
             grid3.add_row(*voucher_zone_row)
             content.add_row(grid3)
        else:
             content.add_row(*voucher_zone_row)
        
        content.add_row("")
        content.add_row(inventory_table)
        content.add_row("")
        content.add_row(Text("Controls: Arrows=Select, Enter=Buy, R=Reroll, N=Next Round", style="dim"))
        
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
            
            # 增强选中状态的视觉反馈
            if is_selected:
                # 移除之前的 card_text.style = "reverse"，改用边框和颜色
                border_style = "bold green"
                if is_cursor:
                    border_style = "bold yellow"
                
                # 在卡牌文本前加一个标记
                # card_text = Text("✓ ", style="bold green") + card_text
                # 这种方式会增加长度，导致内容可能被截断，或者 Panel 宽度不够
                # Panel width is 8. "✓ ♥ 10" is 5-6 chars. Should be fine.
                # 但如果之前内容已经是 "♥ 10"，加上勾选可能有点挤
                
                # 更好的方式：改变 Panel 的 title 或 subtitle
                # 但我们想直观看到牌面不被遮挡
                
                # 或者：只改变边框，不加文本标记，但是把背景色稍微变一下？
                # Rich Panel 不太好直接设背景色，除非用 Style
                
                # 既然用户说“看不到数字了”，说明之前的 "reverse" 导致前景色背景色混淆
                # 现在的 "✓ " 方案其实还行，但要注意不要把牌面挤出去
                
                pass # 保持原样，或者微调
                
            panel = Panel(
                card_text, 
                border_style=border_style, 
                box=box_type,
                width=8,
                height=3,
                title="✓" if is_selected else None, # 尝试用 title 显示勾选
                title_align="right"
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
        
        # Consumables Area (if any)
        if self.game.consumables:
            consumable_row = []
            for i, c in enumerate(self.game.consumables):
                style = "white"
                box_type = box.ROUNDED
                if self.focus_area == "consumables" and i == self.consumable_index:
                    style = "bold magenta"
                    box_type = box.HEAVY
                
                panel = Panel(
                    Text(f"{c.name_cn}\n{c.type.name}", justify="center"),
                    border_style=style,
                    box=box_type,
                    title=f"按回车使用" if self.focus_area == "consumables" and i == self.consumable_index else None
                )
                consumable_row.append(panel)
            
            grid.add_row(
                Table.grid().add_row(*consumable_row)
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
