import tkinter as tk
import time
from datetime import datetime,timedelta
import requests
import threading
import ctypes.wintypes
import tkinter as tk
from datetime import datetime,timedelta
import ctypes, json, time, sys, threading,queue
global saying
pressed_keys = set()
is_hidden = False 
def run_tts(text):
    import asyncio
    import edge_tts
    import os
    import pygame

    OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'example.mp3')
    VOICE = "zh-CN-XiaoxiaoNeural"

    async def amain():
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(OUTPUT_FILE)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(amain())
    loop.close()

    pygame.mixer.init()
    pygame.mixer.music.load("example.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    print(text)
# 初始化 status 变量
status = 1

# 定义值日生名单
names=[]
weekly_schedule=[]
days_in_week = 7
weeks_in_cycle = 4
morning_call = 1
noon_call = 1
morning_call_time = "07:15:00"
noon_call_time = "11:46:00"
with open('config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for key, value in data.items():
    if isinstance(value, dict):
        if 'names' in value:
            names.append(value['names'])
        if 'schedule' in value:
            weekly_schedule.append(f"{key}:{value['schedule']}")
        if 'days_in_week' in value:
            days_in_week = value['days_in_week']
        if 'weeks_in_cycle' in value:
            weeks_in_cycle = value['weeks_in_cycle']
        if 'morning_call' in value:
            morning_call = value['morning_call']
        if 'noon_call' in value:
            noon_call = value['noon_call']
        if 'morning_call_time' in value:
            morning_call_time = value['morning_call_time']
        if 'noon_call_time' in value:
            noon_call_time = value['noon_call_time']
print(names)
print(weekly_schedule)
print(days_in_week)
print(weeks_in_cycle)
print(morning_call)
print(noon_call)
print(morning_call_time)
print(noon_call_time)

# 获取当前周
def get_current_week():
    start_date = "2025-04-28"
    start_ts = time.mktime(time.strptime(start_date, "%Y-%m-%d"))
    days = (time.time() - start_ts) / (24*3600)
    return int(days/7) % weeks_in_cycle

# 获取值日生
get_duty_name = lambda: names[get_current_week()]

# 拆分今日课表
def get_schedule_lines():
    text = weekly_schedule[datetime.now().weekday()]
    if ':' in text:
        day, subs = text.split(':',1)
        items = subs.split('、')
        return [f"{day}:"] + items
    return [text]

# 获取当前时间
get_time = lambda: datetime.now().strftime("%Y年%m月%d日 %A %H:%M:%S")

# 倒计时
status = 1
def countdown(end_times):
    global status
    # 获取当前时间字符串的最后一部分作为时分秒
    time_str = get_time().split()[-1]
    now = datetime.strptime(time_str, "%H:%M:%S")
    for t_str in end_times:
        t = datetime.strptime(t_str, "%H:%M:%S")
        rem = (t - now).total_seconds()
        if rem > 0:
            if rem <= 300:
                status = 1
                m, s = divmod(int(rem), 60)
                return f"距离下课 {t_str} 还有 {m:02d}:{s:02d}"
            if rem < 2400:
                status = 0
                return f"距离下课 {t_str} 还有一段时间"
            status = 1
            # 将下节上课时间调整为原时间提前40分钟
            next_start = (t - timedelta(minutes=40)).strftime("%H:%M:%S")
            return f"下课咯~ 下节上课时间：{next_start}"
    status = 1
    return "放学咯~ 放学愉快！"

# GUI

def create_gui():
    global status
    root = tk.Tk()
    root.overrideredirect(1)
    root.attributes("-topmost", 1)
    root.attributes("-alpha", 0.8)
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    w_main, h_main = 1000, 70
    x_main, y_main = (sw - w_main)//2, 0
    root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")

    # 课表窗口
    sched = tk.Toplevel(root)
    sched.overrideredirect(1)
    sched.attributes("-topmost", 1)
    sched.attributes("-alpha", 0.8)
    w_s, h_s = 70, 280
    x_s, y_s = sw - w_s, (sh - h_s)//2
    sched.geometry(f"{w_s}x{h_s}+{x_s}+{y_s}")

    # 隐藏按钮 for sched
    def hide_sched():
        sched.withdraw()
        sched.after(300000, root.deiconify)#300000
    #btn_s = tk.Button(sched, text="点我隐藏5分钟", command=hide_sched, font=("宋体", 8))
    #btn_s.place(x=5, y=h_s-30)

    # 加载课表
    labels = []
    def load_sched():
        nonlocal labels
        for l in labels:
            l.destroy()
        labels = []
        for i, line in enumerate(get_schedule_lines()):
            lbl = tk.Label(sched, text=line, font=("宋体", 12, "bold"), fg="black", bg=sched["bg"])
            lbl.place(x=5, y=5 + i*25)
            labels.append(lbl)
    load_sched()

    # 拖动支持
    def make_drag(win):
        def start(e):
            win._dx, win._dy = e.x, e.y
        def drag(e):
            win.geometry(f"+{win.winfo_x()-win._dx+e.x}+{win.winfo_y()-win._dy+e.y}")
        win.bind("<ButtonPress-1>", start)
        win.bind("<B1-Motion>", drag)
    make_drag(root)
    make_drag(sched)

    # 同步显示/隐藏
    prev = None
    def sync():
        nonlocal prev
        if status != prev:
            if status == 0:
                root.withdraw()
                sched.withdraw()
            else:
                # 重置主窗口位置
                root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")
                # 重置课表窗口位置
                sched.geometry(f"{w_s}x{h_s}+{x_s}+{y_s}")
                load_sched()
                root.deiconify()
                sched.deiconify()
            prev = status
        root.after(500, sync)

    # 画布 + 隐藏按钮 for main
    canvas = tk.Canvas(root, width=w_main, height=h_main, bd=0, highlightthickness=0)
    canvas.pack()
    def hide_main():
        root.withdraw()
        root.after(300000, root.deiconify)#300000
    #btn_m = tk.Button(root, text="点我隐藏5分钟", command=hide_main, font=("宋体", 10))
    #btn_m.place(x=w_main-550, y=100)
    #btn_m.lift()

    # 更新文字
    def update():
        now = get_time()
        duty = get_duty_name()
        wd = datetime.now().weekday()
        ends = (["8:00:00","9:10:00","10:00:00","10:55:00","11:45:00","13:25:00","14:15:00","15:10:00","16:30:00","17:15:00"] if wd == 4
                else ["8:00:00","9:10:00","10:00:00","10:55:00","11:45:00","13:40:00","14:30:00","15:25:00","16:15:00","17:05:00"])
        rem = countdown(ends)
        canvas.delete("all")
        extra = {4: "享受周末吧~注意包干区哦~", 0: "新周动力加满，小目标逐个击破！", 1: "昨日坚持已赢，今日稳扎稳打！", 2: "半山风景更美，坚持登顶有光！", 3: "破晓前夜最暗，晨光就在转角！"}.get(wd, "享受周末吧~")
        canvas.create_text(w_main/2, 5, text=f"本周值日生：{duty} 值日生们幸苦了~", font=("宋体", 10, "bold"), fill="black", anchor="n")
        #canvas.create_text(w_main/2, 40, text=f"当前时间：{now}", font=("宋体", 20, "bold"), fill="black", anchor="n")
        canvas.create_text(w_main/2, 25, text=f"{rem} {extra}", font=("宋体", 20, "bold"), fill="red", anchor="n")
        canvas.create_text(w_main/2, 55, text=f"隐藏窗口快捷键：F12 + Delete", font=("宋体", 8, "bold"), fill="black", anchor="n")
        time_now = get_time().split()[-1]
        now_now = datetime.strptime(time_now, "%H:%M:%S")
        t = datetime.strptime(morning_call_time, "%H:%M:%S")
        rem_now = (now_now - t).total_seconds()
        if rem_now == 0 and morning_call == 1:

            import requests

            weather_api = "nk4wct2kbw.re.qweatherapi.com"
            api_key = "f2819368bab2496da69272e6c3c86328"

            # 使用 f-string 进行字符串格式化
            weather_url = f"https://{weather_api}/v7/weather/now?location=121.52,31.07&key={api_key}&lang=zh"
            warning_url = f"https://{weather_api}/v7/warning/now?location=121.52,31.07&key={api_key}&lang=zh"

            response = requests.get(weather_url)
            data = response.json()

            warning_response = requests.get(warning_url)
            warning_data = warning_response.json()
            global weather_text
            global weather_temp
            global weather_feelsLike
            global warning_text
            global weather_status
            global warning_status

            if data.get("code") == "200":
                weather_status = 1
                weather_data = data["now"]
                weather_text = weather_data.get('text', '未知')
                weather_temp = weather_data.get('temp', '未知')
                weather_feelsLike = weather_data.get('feelsLike', '未知')


                print(f"天气：{weather_data.get('text', '未知')}")
                print(f"温度：{weather_data.get('temp', '未知')}°C")
                print(f"体感温度：{weather_data.get('feelsLike', '未知')}°C")
            else:
                weather_status = 0
                print(f"获取天气数据失败，错误代码：{data.get('code')}")
                print(f"错误信息：{data.get('message')}")

            if warning_data.get("code") == "200":
                warnings = warning_data.get("warning", [])
                print(warning_data)
                if warnings:
                    for warning in warnings:
                        warning_status = 1
                        warning_text = warning.get('text', '未知')
                        print(f"当前有一条预警信息：{warning.get('text', '未知')}")
                else:
                    warning_status = 0
                    print("当前没有预警信息")
            else:
                print(f"获取预警数据失败，错误代码：{warning_data.get('code')}")
                print(f"错误信息：{warning_data.get('message')}")
            
            
    
            # 替换为你自己的 API 密钥
            
            API_KEY = "57134b293e0ab5e766be4f125b3a6d6e"
            jitang_url = f"https://apis.juhe.cn/fapig/soup/query?key={API_KEY}"
            jitang_response = requests.get(jitang_url)
            jitang_data = jitang_response.json()
            answer = jitang_data["result"]["text"]
            print(answer)
            
            if weather_status ==1 and warning_status == 1:
                saying = f"主人,早上好！，新的一天开始了，今天是{now}，今日天气情况为{weather_text}，温度为{weather_temp}°C,体感温度为{weather_feelsLike}°C，今日有一条预警信息请留意{warning_text}。主人，新的一天到了，送你一句话吧：{answer}"
            if weather_status ==1 and warning_status == 0:

                saying = f"主人,早上好！，新的一天开始了，今天是{now}，今日天气情况为{weather_text}，温度为{weather_temp}°C,体感温度为{weather_feelsLike}°C。主人，新的一天到了，送你一句话吧：{answer}"
            if weather_status ==0:
                saying = f"主人,早上好！，新的一天开始了，今天是{now}，天气情况获取失败。主人，新的一天到了，送你一句话吧：{answer}"  
            threading.Thread(target=run_tts, args=(saying,)).start()

        time_now = get_time().split()[-1]
        now_now = datetime.strptime(time_now, "%H:%M:%S")
        current_weekday = datetime.now().weekday()  # 获取周几
        t_1 = datetime.strptime(noon_call_time, "%H:%M:%S")
        rem_now_1 = (now_now - t_1).total_seconds()
        if 0 <= rem_now_1 < 2 and noon_call == 1:  # 放宽到2秒容差
            if current_weekday == 4:  # 周五
                duty = get_duty_name()
                text = f"主人，中午好，今天是周五，请值日生{duty}注意打扫包赣区。其余的同学们准备好享受周末吧。"
                threading.Thread(target=run_tts, args=(text,), daemon=True).start()
        root.after(1000, update)   
        #窗口快捷键
    event_queue = queue.Queue()
    if sys.maxsize > 2**32:        
        ULONG_PTR = ctypes.c_uint64
    else:
        ULONG_PTR = ctypes.c_uint32 
    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("vkCode", ctypes.wintypes.DWORD),
            ("scanCode", ctypes.wintypes.DWORD),
            ("flags", ctypes.wintypes.DWORD),
            ("time", ctypes.wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]
    WH_KEYBOARD_LL = 13
    WM_KEYDOWN = 0x0100
    VK_CODE = {
    'backspace': 0x08,
    'tab': 0x09,
    'enter': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'pause': 0x13,
    'capslock': 0x14,
    'esc': 0x1B,
    'space': 0x20,
    'pageup': 0x21,
    'pagedown': 0x22,
    'end': 0x23,
    'home': 0x24,
    'left': 0x25,
    'up': 0x26,
    'right': 0x27,
    'down': 0x28,
    'insert': 0x2D,
    'delete': 0x2E,
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'a': 0x41,
    'b': 0x42,
    'c': 0x43,
    'd': 0x44,
    'e': 0x45,
    'f': 0x46,
    'g': 0x47,
    'h': 0x48,
    'i': 0x49,
    'j': 0x4A,
    'k': 0x4B,
    'l': 0x4C,
    'm': 0x4D,
    'n': 0x4E,
    'o': 0x4F,
    'p': 0x50,
    'q': 0x51,
    'r': 0x52,
    's': 0x53,
    't': 0x54,
    'u': 0x55,
    'v': 0x56,
    'w': 0x57,
    'x': 0x58,
    'y': 0x59,
    'z': 0x5A,
    'f1': 0x70,
    'f2': 0x71,
    'f3': 0x72,
    'f4': 0x73,
    'f5': 0x74,
    'f6': 0x75,
    'f7': 0x76,
    'f8': 0x77,
    'f9': 0x78,
    'f10': 0x79,
    'f11': 0x7A,
    'f12': 0x7B,
    'numlock': 0x90,
    'scrolllock': 0x91
    }
    VK_F12 = VK_CODE['f12']  # F12 键的虚拟键码
    VK_DELETE = VK_CODE['delete']  # DELETE 键的虚拟键码
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    pressed_keys = set()
    is_hidden = False
    def toggle_window():
        global is_hidden
        if is_hidden:
        # 重置主窗口位置
            root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")
            root.deiconify()
            # 重置课表窗口位置
            sched.geometry(f"{w_s}x{h_s}+{x_s}+{y_s}")
            sched.deiconify()
        else:
            root.withdraw()
            sched.withdraw()
        is_hidden = not is_hidden

    @ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)
    def low_level_keyboard_proc(nCode, wParam, lParam):
        if nCode == 0:
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = kb.vkCode
            if wParam == WM_KEYDOWN:
                pressed_keys.add(vk)
                if VK_F12 in pressed_keys and VK_DELETE in pressed_keys:
                    event_queue.put("TOGGLE_WINDOW")
            elif wParam == 0x0101:  
                pressed_keys.discard(vk)
        return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.POINTER(ctypes.c_void_p)))
    hook_id = user32.SetWindowsHookExW(
        WH_KEYBOARD_LL,
        low_level_keyboard_proc,
        None, 
        0
    )
    def check_events():
        try:
            while True:
                event = event_queue.get_nowait()
                if event == "TOGGLE_WINDOW":
                    toggle_window()
        except queue.Empty:
            pass
        root.after(100, check_events)
    root.deiconify() 
    def win32_message_loop():
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    thread = threading.Thread(target=win32_message_loop)
    thread.daemon = True  
    thread.start()
        
    

    sync()
    update()
    check_events()
    root.mainloop()


if __name__ == "__main__":
    create_gui()
