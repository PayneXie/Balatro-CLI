import sys
import os
from balatro.game import Game
from balatro.ui import TUI

def main():
    # 检查是否在交互式终端运行
    # 在某些IDE或后台进程中，sys.stdin.isatty() 可能为 False
    if not sys.stdin.isatty():
        print("警告: 检测到非交互式终端环境。")
        print("TUI 界面需要真实的终端环境支持 (如 CMD, PowerShell)。")
        print("如果您在 IDE 的内置运行窗口中看不到内容，请尝试在外部终端中运行此脚本。")
        print("-" * 50)

    print("正在启动 Balatro CLI TUI...")
    print("请确保您在支持 ANSI 颜色的终端中运行 (Windows 推荐使用 Windows Terminal / PowerShell)")
    
    # 给用户一点时间看提示
    import time
    time.sleep(1)

    game = Game()
    ui = TUI(game)
    try:
        ui.run()
    except KeyboardInterrupt:
        # 确保退出时恢复光标等
        print("\n游戏已中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
