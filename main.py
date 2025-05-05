import tkinter as tk
import time
from datetime import datetime,timedelta
import requests
import threading
global saying
def run_tts(text):
    import asyncio
    import edge_tts
    import playsound
    import os

    OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'example.mp3')
    VOICE = "zh-CN-XiaoxiaoNeural"

    async def amain():
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(OUTPUT_FILE)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(amain())
    loop.close()

    playsound.playsound("example.mp3")
    print(text)
# 初始化 status 变量
status = 1

# 定义值日生名单
names = [
    "王钰婷#，黄馨远#，周迦遥，郭菲而，王芝馨，罗一蕃，陈佳宜，康丰翼，黎浩楠，付乘瑞",
    "张静诚#，张宇琛#，陶宇辰，倪瑞雯，宋思颖，陆思旭，黄子扬，唐思淇，万思妤，吴欣宸",
    "王谦#，李昳凡#，章楚明，邰宇晨，郭莫非，郭晓桐，卢傲天，周佳怡，易欣媛，黄敬涵",
    "夏明辉#，汤一卓#，涂舒扬，黄梅雪，柯雯晨，程天玥，徐逸扬，陈乐瑶，陈子卉，陈子卉"
]

# 定义一周的课表
weekly_schedule = [
    "周一：化学、数学、数学、物理、化学、化学、数学、数学、物理、化学",
    "周二：数学、英语、历史、生物、体育、化学、数学、数学、物理、化学",
    "周三：英语、地理、物理、化学、音乐、化学、数学、数学、物理、化学",
    "周四：语文、数学、政治、历史、美术、化学、数学、数学、物理、化学",
    "周五：英语、物理、化学、体育、自习、化学、数学、数学、物理、化学",
    "周六：无",
    "周日：无"
]

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
    if '：' in text:
        day, subs = text.split('：',1)
        items = subs.split('、')
        return [f"{day}："] + items
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
    w_main, h_main = 1000, 130
    x_main, y_main = (sw - w_main)//2, 0
    root.geometry(f"{w_main}x{h_main}+{x_main}+{y_main}")

    # 课表窗口
    sched = tk.Toplevel(root)
    sched.overrideredirect(1)
    sched.attributes("-topmost", 1)
    sched.attributes("-alpha", 0.8)
    w_s, h_s = 90, 320
    x_s, y_s = 0, (sh - h_s)//2
    sched.geometry(f"{w_s}x{h_s}+{x_s}+{y_s}")

    # 隐藏按钮 for sched
    def hide_sched():
        sched.withdraw()
        sched.after(300000, sched.deiconify)
    btn_s = tk.Button(sched, text="点我隐藏5分钟", command=hide_sched, font=("宋体", 8))
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
    def hide_main():
        root.withdraw()
        root.after(300000, root.deiconify)
    btn_m = tk.Button(root, text="点我隐藏5分钟", command=hide_main, font=("宋体", 10))
    btn_m.place(x=w_main-550, y=100)
    btn_m.lift()

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
        canvas.create_text(w_main/2, 20, text=f"本周值日生：{duty} {extra}", font=("宋体", 10, "bold"), fill="black", anchor="n")
        canvas.create_text(w_main/2, 40, text=f"当前时间：{now}", font=("宋体", 20, "bold"), fill="black", anchor="n")
        canvas.create_text(w_main/2, 70, text=f"{rem} {extra}", font=("宋体", 20, "bold"), fill="red", anchor="n")
        time_now = get_time().split()[-1]
        now_now = datetime.strptime(time_now, "%H:%M:%S")
        t = datetime.strptime("15:31:20", "%H:%M:%S")
        rem_now = (now_now - t).total_seconds()
        if rem_now == 0 :

            import requests

            weather_api = "your_api"
            api_key = "your_key"

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
            
            API_KEY = "your_api"
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


            
            
        root.after(1000, update)

    sync()
    update()
    root.mainloop()

if __name__ == "__main__":
    create_gui()
