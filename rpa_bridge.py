import pyautogui
import pyperclip
import pygetwindow as gw
import time
import sys
import subprocess

def run_gui_logic(model_path):
    pat_exe = r"C:\PAT351\PAT 3.exe"
    
    subprocess.Popen([pat_exe, model_path])
    time.sleep(8) 
    
    pyautogui.press('alt')
    time.sleep(0.5)
    
    try:
        pat_windows = gw.getWindowsWithTitle('PAT')
        if pat_windows:
            win = pat_windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            win.maximize()
    except Exception:
        pass # 删掉所有多余的中文报错打印，防止编码崩溃
        
    time.sleep(1.5) 

    # 3. 运行验证 (F7)
    pyautogui.press('f7')
    time.sleep(1.5) # 等待验证弹窗出来
    
    # === RPA 盲操连招：处理验证弹窗 ===
    # 按一下下方向键，确保选中列表里的第一个断言
    pyautogui.press('down')
    time.sleep(0.5)
    
    pyautogui.press('tab')
    time.sleep(0.5)

    pyautogui.press('enter')
    # ==================================

    # 验证计算时间，等长一点 (取决于模型复杂度，6-10秒)
    time.sleep(5) 

    pyautogui.press('tab') 
    time.sleep(0.5)
    
    pyautogui.press('tab') 
    time.sleep(0.5)
    
    pyautogui.press('tab') 
    time.sleep(0.5)

    pyautogui.press('tab') 
    time.sleep(0.5)

    pyautogui.press('tab') 
    time.sleep(0.5)

    # 4. 提取结果 (在弹窗跑完结果后，直接全选复制)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    
    # 5. 关闭 PAT (连按两次 Alt+F4：第一次关弹窗，第二次关主程序)
    pyautogui.hotkey('alt', 'f4')
    time.sleep(0.5)
    pyautogui.hotkey('alt', 'f4')

    return pyperclip.paste()

if __name__ == "__main__":
    # 【终极防弹衣】强制将整个 Python 输出流切换为 UTF-8，彻底免疫任何乱码！
    sys.stdout.reconfigure(encoding='utf-8')
    
    if len(sys.argv) > 1:
        target_model = sys.argv[1]
        final_raw = run_gui_logic(target_model)
        print(final_raw)