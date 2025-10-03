import win32gui
import win32con
import win32api
import time
import os
import sys
import io
from PIL import ImageGrab
import subprocess
import ctypes
import argparse

if sys.stdout.encoding is None or sys.stdout.encoding.lower().replace('-', '') != 'utf8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)  #解决webui显示字符问题


def sign_out_wechat():
    """
    强制关闭现有微信进程。
    """
    process_names = ["WeChat.exe", "Weixin.exe"]
    print("正在尝试关闭现有的微信进程...")
    for process_name in process_names:
        os.system(f'taskkill /F /IM {process_name} > nul 2>&1')
    time.sleep(1)
    print("微信进程已关闭。")


def sign_out_bot():
    """
    强制关闭 bot.py 进程。
    """
    print("正在尝试关闭 bot.py 进程...")
    # 使用 wmic 命令通过命令行内容查找并终止进程，比直接杀掉 python.exe 更安全
    os.system('wmic process where "name=\'python.exe\' and commandline like \'%bot.py%\'" delete > nul 2>&1')
    print("bot.py 进程已关闭。")


def set_dpi_awareness():
    """
    设置进程为 DPI 感知，解决在高分屏上的截图错位问题。
    """
    try:
        # 尝试使用 Windows 8.1 及以上版本的 API
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # 2 = PROCESS_PER_MONITOR_DPI_AWARE
        print("已设置为 Per-Monitor DPI Aware。")
    except AttributeError:
        # 如果失败，回退到旧版本的 API
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            print("已设置为 System DPI Aware。")
        except AttributeError:
            print("警告：无法设置 DPI 感知，在高分屏上截图可能会错位。")


def force_set_foreground_window(hwnd):
    """
    一个更强大的 SetForegroundWindow 版本，用于解决权限问题。
    """
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    time.sleep(0.1)
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    except Exception as e:
        print(f"SetForegroundWindow 失败: {e}")
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)


def restart_and_find_wechat():
    """
    强制关闭现有微信进程，然后重新启动它。
    """
    process_names = ["WeChat.exe", "Weixin.exe"]
    
    print("正在尝试关闭现有的微信进程...")
    for process_name in process_names:
        os.system(f'taskkill /F /IM {process_name} > nul 2>&1')
    time.sleep(1) 

    possible_paths = [
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Tencent\\WeChat\\WeChat.exe"),
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Tencent\\WeChat\\WeChat.exe"),
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Tencent\\Weixin\\Weixin.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Tencent\\Weixin\\Weixin.exe"),
    ]
    
    wechat_path = None
    for path in possible_paths:
        if os.path.exists(path):
            wechat_path = path
            break
            
    if not wechat_path:
        print("错误：未在常见位置找到微信 (WeChat.exe)。")
        return False

    print(f"已找到微信，路径: {wechat_path}")
    print("正在启动微信...")
    try:
        subprocess.Popen([wechat_path])
        print("微信已启动，请等待登录窗口出现...")
        # 等待时间加长一点，确保窗口完全渲染
        time.sleep(5) 
        return True
    except Exception as e:
        print(f"启动微信时出错: {e}")
        return False

def click_wechat_buttons_and_screenshot():
    if not restart_and_find_wechat():
        return

    script_directory = os.path.dirname(os.path.abspath(__file__))
    fixed_file_name = "wechat_latest_screenshot.png"
    file_path = os.path.join(script_directory, fixed_file_name)
    print(f"截图将保存在脚本所在目录: {script_directory}")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"已清除旧的截图文件: {file_path}")
        except Exception as e:
            print(f"清除旧文件时出错: {e}")
    
    hwnd = 0
    for i in range(10): 
        hwnd = win32gui.FindWindow(None, "微信")
        if hwnd != 0:
            print("已找到微信登录窗口。")
            break
        time.sleep(1)
    
    if hwnd == 0:
        print("超时：找不到微信登录窗口。")
        return False
    
    print("正在激活微信窗口...")
    force_set_foreground_window(hwnd)

    # 获取窗口位置和大小
    try:
        # 确保窗口激活后位置信息是最终的
        time.sleep(0.5) 
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        # 防止窗口大小为0或负数
        if width <= 0 or height <= 0:
            print(f"获取到的窗口大小无效 (宽:{width}, 高:{height})，程序终止。")
            return False
    except Exception as e:
        print(f"获取窗口矩形时出错: {e}")
        return False

    # 第一次点击：二维码中心
    confirm_x = width // 2
    confirm_y = height // 2 + 50 
    win32api.SetCursorPos((left + confirm_x, top + confirm_y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("已点击二维码区域以激活。")
    
    time.sleep(0.5)

    # 第二次点击："登录"按钮
    login_x = width // 2
    login_y = height - 100 
    win32api.SetCursorPos((left + login_x, top + login_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("已点击登录按钮。")

    print("正在等待主窗口并准备截图...")
    # 等待时间加长，确保主窗口完全加载并渲染
    time.sleep(3) 

    hwnd_main = win32gui.FindWindow("WeChatMainWndForPC", "微信")
    if hwnd_main == 0:
        print("未找到微信主窗口，将截取原登录窗口区域。")
        bbox = (left, top, right, bottom)
    else:
        print("找到主窗口，准备截取主窗口。")
        force_set_foreground_window(hwnd_main)
        time.sleep(0.5) # 同样等待一下确保位置稳定
        left, top, right, bottom = win32gui.GetWindowRect(hwnd_main)
        bbox = (left, top, right, bottom)

    # 截取指定区域
    screenshot = ImageGrab.grab(bbox=bbox)
    
    screenshot.save(file_path)
    print(f"截图成功！已保存到: {file_path}")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="微信自动登录和机器人启动脚本")
    parser.add_argument("-login", action="store_true", help="仅启动微信并登录")
    parser.add_argument("-signout", action="store_true", help="仅关闭微信进程")
    parser.add_argument("-bot", action="store_true", help="在启动微信时同时启动bot.py")
    parser.add_argument("-botout", action="store_true", help="在关闭微信时同时关闭bot.py")

    args = parser.parse_args()

    set_dpi_awareness()

    if args.login:
        print("执行登录操作...")
        if click_wechat_buttons_and_screenshot():
            if args.bot:
                print("微信登录流程已启动，等待15秒以确保登录完成...")
                time.sleep(15)
                print("等待结束，现在启动 bot.py...")
                try:
                    # bot.py 在当前目录
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    bot_path = os.path.join(current_dir, "bot.py")
                    if os.path.exists(bot_path):
                        subprocess.Popen([sys.executable, bot_path])
                        print("bot.py 已启动。")
                    else:
                        print(f"错误: 未找到 bot.py at {bot_path}")
                except Exception as e:
                    print(f"启动 bot.py 时出错: {e}")
    elif args.signout:
        print("执行登出操作...")
        sign_out_wechat()
        if args.botout:
            sign_out_bot()
    else:
        print("没有提供有效参数。请使用 -login 或 -signout。")
        print("用法示例:")
        print("  python Relogin.py -login")
        print("  python Relogin.py -login -bot")
        print("  python Relogin.py -signout")
        print("  python Relogin.py -signout -botout")