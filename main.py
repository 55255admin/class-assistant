import tkinter as tk
import time
from datetime import datetime,timedelta
import ctypes
import json

pressed_keys = set()
is_hidden = False 

# 初始化 status 变量
status = 1


#读取值日生名单与课表
names=[]
weekly_schedule=[]
with open('config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for day, info in data.items():
    if isinstance(info, dict) and 'schedule' in info:
        weekly_schedule.append(f"{day}:{info['schedule']}")
for group, info in data.items():
    if isinstance(info, dict) and 'names' in info:
        names.append(info['names'])   


days_in_week = 7
weeks_in_cycle = 4

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
    #root.attributes("-alpha", 0.99)
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    w_main, h_main = 1000, 100
    x_main, y_main = (sw - w_main)//2, 0
    root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")

    # 课表窗口
    sched = tk.Toplevel(root)
    sched.overrideredirect(1)
    sched.attributes("-topmost", 1)
    w_s, h_s = 90, 320
    x_s, y_s = 0, (sh - h_s)//2
    sched.geometry(f"{w_s}x{h_s}+{x_s}+{y_s}")
    

    # 隐藏按钮 for sched
    def hide_sched():
        sched.withdraw()
        sched.after(300000, sched.deiconify)
    btn_s = tk.Button(sched, text="F12+del隐藏", command=hide_sched, font=("宋体", 8))
    btn_s.place(x=5, y=h_s-30)

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
    '''def make_drag(win):
        def start(e):
            win._dx, win._dy = e.x, e.y
        def drag(e):
            win.geometry(f"+{win.winfo_x()-win._dx+e.x}+{win.winfo_y()-win._dy+e.y}")
        win.bind("<ButtonPress-1>", start)
        win.bind("<B1-Motion>", drag)
    make_drag(root)
    make_drag(sched)'''

    # 同步显示/隐藏
    prev = None
    def sync():
        nonlocal prev
        if status != prev:
            if status == 0:
                root.withdraw()
                sched.withdraw()
            else:
                root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")
                sched.geometry(f"{w_s}x{h_s}+{x_s}+{y_s}")
                load_sched()
                root.deiconify()
                sched.deiconify()
            prev = status
        root.after(500, sync)

    # 画布 + 隐藏按钮 for main
    canvas = tk.Canvas(root, width=w_main, height=h_main, bd=0, highlightthickness=0)
    canvas.pack()
    '''def hide_main():
        root.withdraw()
        root.after(300000, root.deiconify)
    btn_m = tk.Button(root, text="点我隐藏5分钟", command=hide_main, font=("宋体", 10))
    btn_m.place(x=w_main-550, y=100)
    btn_m.lift()'''
    # 更新文字
    def update():
        now = get_time()
        duty = get_duty_name()
        wd = datetime.now().weekday()
        ends = (["8:00:00","9:10:00","10:00:00","10:55:00","11:45:00","13:25:00","14:15:00","15:10:00","16:00:00","17:15:00"] if wd == 4
                else ["8:00:00","9:10:00","10:00:00","10:55:00","11:45:00","13:40:00","14:30:00","15:25:00","16:15:00","17:05:00"])
        rem = countdown(ends)
        canvas.delete("all")
        extra = {4: "享受周末吧~注意包干区哦~", 0: "新周动力加满，小目标逐个击破！", 1: "昨日坚持已赢，今日稳扎稳打！", 2: "半山风景更美，坚持登顶有光！", 3: "破晓前夜最暗，晨光就在转角！"}.get(wd, "享受周末吧~")
        canvas.create_text(w_main/2, 10, text=f"本周值日生：{duty} {extra}", font=("宋体", 10, "bold"), fill="black", anchor="n")
        canvas.create_text(w_main/2, 30, text=f"当前时间：{now}", font=("宋体", 20, "bold"), fill="black", anchor="n")
        canvas.create_text(w_main/2, 60, text=f"{rem} {extra}", font=("宋体", 20, "bold"), fill="red", anchor="n")
        root.after(1000, update)

    sync()
    update()

    #窗口快捷键
    def shortcut():
        listener = tk.Toplevel()
        listener.overrideredirect(True)
        listener.geometry("1x1+0+0")
        listener.attributes("-alpha", 0.0)
        listener.attributes("-topmost", True)
        listener.focus_force()

        def on_key_press(event):
            pressed_keys.add(event.keysym.lower())
            # 判断 F12 + Delete
            if 'f12' in pressed_keys and 'delete' in pressed_keys:
                global is_hidden
                if is_hidden:
                    root.deiconify()
                    sched.deiconify()
                else:
                    root.withdraw()
                    sched.withdraw()
                is_hidden = not is_hidden

        def on_key_release(event):
            pressed_keys.discard(event.keysym.lower())

    
        listener.bind_all("<KeyPress>", on_key_press)
        listener.bind_all("<KeyRelease>", on_key_release)

    shortcut()


    #窗口透明
    def transparency():
        root.update_idletasks()
        sched.update_idletasks()
        GWL_EXSTYLE       = -20
        WS_EX_LAYERED     = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        LWA_ALPHA         = 0x00000002
        
        
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd, GWL_EXSTYLE,
            style | WS_EX_LAYERED | WS_EX_TRANSPARENT
        )
        ctypes.windll.user32.SetLayeredWindowAttributes(
            hwnd, 0, int(0.8 * 255), LWA_ALPHA
        )
        hwnd1 = ctypes.windll.user32.GetParent(sched.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd1, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd1, GWL_EXSTYLE,
            style | WS_EX_LAYERED | WS_EX_TRANSPARENT
        )
        ctypes.windll.user32.SetLayeredWindowAttributes(
            hwnd1, 0, int(0.8 * 255), LWA_ALPHA
        )
    
    transparency()
    
    root.mainloop()
    


if __name__ == "__main__":
    create_gui()
