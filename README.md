# - Hello~前言
本人担任电教委员一职，因忘记打扫包干区而被罚打扫教室，因此一怒之下做了这个程序，供各位有需要帮助的人提供。大部分地方已写上注释，应该很好理解。
如果喜欢的话，还请给个Star~
注：本项目使用AGPL协议，因此如有修改还请开源哦~，建议直接发到 pull request上。
# - 使用说明
1.请直接下载main.py文件。确保电脑上已安装好python。
2.在第9行修改值日生列表。
![image](https://github.com/user-attachments/assets/d661b09b-4708-4c1e-b550-a9a7899d5eae)

3.在第17行修改课表。
![image](https://github.com/user-attachments/assets/cbcb4fa7-dc88-436c-936b-ebad30d17667)
4.第27行代表当前值日生持续几天，28行表示几个循环为一个周期。
![image](https://github.com/user-attachments/assets/1a0c7202-3442-462b-99e9-6b918b3519cb)
例如：本程序为当前值日生连续工作7天。每四周（4个7天）为一周期循环。
5.本程序采取一节课时间为40分钟。因此需要修改时间请到54行的函数中修改。
![image](https://github.com/user-attachments/assets/e47b6f3f-8bb2-4fa7-992b-e5e6fbbeedbd)
例如第63行为300秒，（距离下课5分钟显示窗口并倒计时），67行为2400秒（上课时隐藏窗口，因前一个if先触发，因此倒计时5分钟会直接显示。如要改成对应时间，例：35分钟。即改成35*60），72行的minutes也改成对应时间如35。
6.在第161行修改为下课时间。第一个列表是除周五以外的时间，第二个是周五的时间。如需修改请修改对应“wd == 4”部分。
![image](https://github.com/user-attachments/assets/5cb027b8-98fa-4a41-adf5-d83f0a77fbd9)
165行为对应标语，请酌情修改。
附：wd值与星期的对应关系：
|wd|星期|
|--|--|
|0|周一|
|1|周二|
|2|周三|
|3|周四|
|4|周五|
|5|周六|
|6|周天|
# - 日志
- [x] 2025.4.30 完成初步程序
- [ ] 2025.5.3 增加LGM模型api，实现早晨报早安功能。
- [ ] 2025.5.4 合并Resigned版本

