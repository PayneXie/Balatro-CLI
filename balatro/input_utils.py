import sys
import os
import time

class Key:
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    ENTER = 'ENTER'
    SPACE = 'SPACE'
    ESCAPE = 'ESCAPE'
    # Other keys will be returned as their string representation, e.g. 'q', 'i', 'F'

class InputHandler:
    def __init__(self):
        self.is_windows = os.name == 'nt'
        self.old_settings = None
        
        if self.is_windows:
            import msvcrt
            self.msvcrt = msvcrt
        else:
            import tty
            import termios
            import select
            self.tty = tty
            self.termios = termios
            self.select = select

    def start(self):
        """进入 Raw 模式 (Linux/Mac)"""
        if not self.is_windows:
            self.fd = sys.stdin.fileno()
            self.old_settings = self.termios.tcgetattr(self.fd)
            # 使用 setcbreak 而不是 setraw，避免完全禁用信号（如 Ctrl+C）
            # setcbreak 也会禁用回显和行缓冲
            self.tty.setcbreak(self.fd)

    def stop(self):
        """恢复终端设置 (Linux/Mac)"""
        if not self.is_windows and self.old_settings:
            self.termios.tcsetattr(self.fd, self.termios.TCSADRAIN, self.old_settings)

    def has_input(self):
        if self.is_windows:
            return self.msvcrt.kbhit()
        else:
            # 在 raw/cbreak 模式下，可以直接 select
            dr, dw, de = self.select.select([sys.stdin], [], [], 0)
            return bool(dr)

    def get_key(self):
        if not self.has_input():
            return None
            
        if self.is_windows:
            key = self.msvcrt.getch()
            if key == b'\xe0': # Arrow prefix
                key = self.msvcrt.getch()
                if key == b'H': return Key.UP
                if key == b'P': return Key.DOWN
                if key == b'K': return Key.LEFT
                if key == b'M': return Key.RIGHT
                return None
            
            if key == b'\r': return Key.ENTER
            if key == b' ': return Key.SPACE
            if key == b'\x1b': return Key.ESCAPE
            
            try:
                return key.decode('utf-8')
            except:
                return None
        else:
            # Linux implementation
            # 此时终端已经在 start() 中被置为 raw/cbreak 模式
            # 直接读取即可
            
            ch = sys.stdin.read(1)
            
            if ch == '\x1b':
                # Check for sequence
                # 由于是非阻塞检查，可能需要一点点延迟等待序列后续字符
                # 但 select 已经告诉我们有输入了
                # 这里再次用 select 检查是否有后续字符（序列通常是一次性发过来的）
                dr, _, _ = self.select.select([sys.stdin], [], [], 0.01)
                if not dr:
                    return Key.ESCAPE
                    
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return Key.UP
                    if ch3 == 'B': return Key.DOWN
                    if ch3 == 'C': return Key.RIGHT
                    if ch3 == 'D': return Key.LEFT
                return Key.ESCAPE # Fallback
            
            if ch == '\r' or ch == '\n': return Key.ENTER
            if ch == ' ': return Key.SPACE
            return ch
