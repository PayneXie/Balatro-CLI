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

    def has_input(self):
        if self.is_windows:
            return self.msvcrt.kbhit()
        else:
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
            fd = sys.stdin.fileno()
            old_settings = self.termios.tcgetattr(fd)
            try:
                self.tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                
                if ch == '\x1b':
                    # Check for sequence
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
                
            finally:
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old_settings)
