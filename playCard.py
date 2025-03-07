import subprocess
import time
import setting
import datetime
import smtplib
import os
import time
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger 
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


go_hour = int(setting.go_hour)
back_hour = int(setting.back_hour)
directory = setting.directory
sender = setting.sender
psw = setting.psw
receive = setting.receive
screen_dir = setting.screen_dir


# 打开钉钉以及关闭钉钉封装为一个妆饰器函数
def with_open_close_dingding(func):
    def wrapper(self, *args, **kwargs):
        t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print(f"\n{t} 开始")
        print('点亮屏幕，解锁，打开钉钉中...')
        operation_list = [self.adbpower, self.adbclear, self.adbopen_dingding]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        # 确保完全启动，并且加载上相应按键（根据手机响应速度可以调整这里）
        time.sleep(15)
        
        print("打开打卡界面中...")
        self.screencap('dingding_home')
        operation_list1 = [self.adbselect_work, self.adbselect_work, self.adbselect_playcard]
        for operation in operation_list1:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            # 等待点击屏幕后响应
            time.sleep(5)
        # 等待工作页面加载
        time.sleep(20)
        self.screencap('playcard_interface')
        
        # print("执行打卡操作")
        func(self, *args, **kwargs)
        
        print("返回桌面，退出钉钉，手机黑屏中...")
        operation_list2 = [self.adbback_index, self.adbkill_dingding, self.adbpower]
        for operation in operation_list2:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print(f"\n{t} 结束")

    return wrapper


class dingDing:
    def __init__(self, directory):
        self.directory = directory
        # 点亮屏幕
        self.adbpower = 'adb shell input keyevent 26'
        # 滑屏解锁
        self.adbclear = 'adb shell input swipe %s' % (setting.light_position)
        # 启动钉钉应用
        self.adbopen_dingding = 'adb shell monkey -p com.alibaba.android.rimet -c android.intent.category.LAUNCHER 1'
        # 关闭钉钉
        self.adbkill_dingding = 'adb shell am force-stop com.alibaba.android.rimet'
        # 返回桌面
        self.adbback_index = 'adb shell input keyevent 3'
        # 点击工作
        self.adbselect_work = 'adb shell input tap %s' % (setting.work_position)
        # 点击考勤打卡
        self.adbselect_playcard = 'adb shell input tap %s' % (setting.card_position)
        # 点击打卡
        self.adbclick_playcard = 'adb shell input tap %s' % (setting.play_position)

    def test_device(self):
        operation_list = [self.adbpower, self.adbclear, self.adbpower]
        print('点亮屏幕，解锁，关闭屏幕')
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(1)

    # 1 点亮屏幕 》》解锁 》》打开钉钉
    def open_dingding(self):
        operation_list = [self.adbpower, self.adbclear, self.adbopen_dingding]
        print('点亮屏幕，解锁，打开钉钉中...')
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        # 确保完全启动，并且加载上相应按键
        time.sleep(15)
        print("成功打开钉钉")
        self.screencap("dingding_home")

    # 2 打开打卡界面
    def openplaycard_interface(self):
        print("打开打卡界面中...")
        operation_list = [self.adbselect_work, self.adbselect_work, self.adbselect_playcard]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
        time.sleep(20)
        print("成功打开打卡界面")
        self.screencap('playcard_interface')

    # 3 截屏>> 发送到电脑 >> 删除手机中保存的截屏
    def screencap(self, name):
        print(f"截屏{name}, 发送至电脑中...")
        # 设备截屏保存到sdcard
        adbscreencap = f'adb shell screencap -p sdcard/{name}.png'
        # 传送到计算机
        adbpull = f'adb pull sdcard/{name}.png {screen_dir}'
        # 删除设备截屏
        adbrm_screencap = f'adb shell rm -r sdcard/{name}.png'
        operation_list = [adbscreencap, adbpull, adbrm_screencap]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print(f"成功发送<<{name}>>至电脑")

    # 4 发送邮件（QQ邮箱）
    @staticmethod
    def send_email(send_all=True, *need_send_filenames):
        """
        qq邮箱 需要先登录网页版，开启SMTP服务。获取授权码，A function that takes a boolean as the first argument and optionally an array as the second argument,
        depending on the value of the first argument.

        :param is_true: A boolean indicating whether to expect an additional array parameter.
                        - If `True`, no other arguments should be provided.
                        - If `False`, a single list argument should follow.

        :param args: A variable number of arguments. When `is_true` is `False`, it expects exactly one list argument.

        :raises AssertionError: If the correct number or type of arguments is not provided based on the value of `is_true`.

        :example:
            >>> send_email(True)  # Correct usage when expecting no additional arguments.
            First argument is True and no array is passed.

            >>> send_email()  # Correct usage when expecting no additional arguments.
            First argument is True and no array is passed.

            >>> send_email(False, 1, 2, 3)  # Correct usage when expecting a list argument.
            First argument is False and an array was passed: [1, 2, 3]

            >>> send_email(False)  # Incorrect usage, missing the required list argument.
            Traceback (most recent call last):
                ...
            AssertionError: When the first argument is False, a single list argument should be provided

            >>> send_email(True, 1, 2, 3)  # Incorrect usage, providing extra arguments with 'True'.
            Traceback (most recent call last):
                ...
            AssertionError: When the first argument is True, no other arguments should be provided
        """
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        message = MIMEMultipart('related')
        subject = now_time + '打卡'
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = receive

        # Attach images
        content_html = '<html><body>'
        
        if send_all:
            for filename in os.listdir(screen_dir):
                if filename.endswith('.png'):
                    with open(os.path.join(screen_dir, filename), 'rb') as file:
                        img_data = file.read()
                        file.close()
                        if img_data:
                            content_html += f'<p>{filename}</p>'
                            content_html += f'<img src="cid:{filename}" alt="{filename}"><br>'
                            img = MIMEImage(img_data)
                            img.add_header('Content-ID', f'<{filename}>')
                            message.attach(img)
        else:
            for filename in need_send_filenames:
                with open(os.path.join(screen_dir, filename), 'rb') as file:
                    img_data = file.read()
                    file.close()
                    if img_data:
                        content_html += f'<p>{filename}</p>'
                        content_html += f'<img src="cid:{filename}" alt="{filename}"><br>'
                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', f'<{filename}>')
                        message.attach(img)
    
        content_html += '</body></html>'
        content = MIMEText(content_html, 'html', 'utf-8')
        message.attach(content)
        try:
            server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            server.login(sender, psw)
            server.sendmail(sender, receive, message.as_string())
            server.quit()
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print(e)

    # 5 返回桌面 》》 退出钉钉 》》 手机黑屏
    def close_dingding(self):
        operation_list = [self.adbback_index, self.adbkill_dingding, self.adbpower]
        print("返回桌面，退出钉钉，手机黑屏中...")
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print("成功关闭钉钉并锁屏")

    # 手动点击打开
    def click_playcard(self):
        print("打卡")
        operation_list = [self.adbclick_playcard]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(3)
        print("完成打卡")
        self.screencap('result')
        

    # 上班(极速打卡)
    @with_open_close_dingding
    def goto_work(self):
        self.send_email()
        print("上班打卡成功")

    # 下班
    @with_open_close_dingding
    def off_work(self):
        operation_list = [self.adbclick_playcard]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(3)
        self.send_email()
        print("下班打卡成功")

#####################################################################################################

def auto_playCard(num):
    scheduler = BlockingScheduler()

    # 一周早上
    trigger = CronTrigger(day_of_week='mon-fri', hour=9, minute=23, jitter=240)
    scheduler.add_job(dingDing(directory).goto_work, trigger=trigger)

    if num == 1:
        # 全
        trigger = CronTrigger(day_of_week='mon-fri', hour=21, minute=0, jitter=300)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 2:
        # [一五]21:00
        # [二三]21:30
        trigger = CronTrigger(day_of_week='mon,fri', hour=21, minute=0, jitter=300)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='tue,wed', hour=21, minute=30, jitter=240)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 3:
        # [一二三]21:30
        # [五]21:00
        trigger = CronTrigger(day_of_week='mon,tue,wed', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='fri', hour=21, minute=0, jitter=300)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 4:
        # [一二]21:30
        # [四]21:00
        trigger = CronTrigger(day_of_week='mon,tue', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='thu', hour=21, minute=0, jitter=120)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 5:
        # [二三]21:00
        # [四]21:30
        trigger = CronTrigger(day_of_week='tue,wed', hour=21, minute=0, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='thu', hour=21, minute=30, jitter=120)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 6:
        # [二四]21:30
        trigger = CronTrigger(day_of_week='tue,thu', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 7:
        # [三四]21:00
        trigger = CronTrigger(day_of_week='wed', hour=21, minute=00, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='thu', hour=21, minute=00, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 8:
        # [一二]21:30
        # [三]21：00
        # [四]22：30
        # [五]22:00
        trigger = CronTrigger(day_of_week='mon,tue', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='wed', hour=21, minute=00, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='thu', hour=22, minute=30, jitter=200)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='fri', hour=22, minute=0, jitter=600)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    else:
        trigger = CronTrigger(day_of_week='tue', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)

    scheduler.start()

def handling():
        operation_list = ['adb shell input keyevent 26']
        print('熄灭屏幕')
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()

# 钉钉意外退出，重新登录钉钉
def relogin_dingding():
    d = dingDing(directory)
    d.open_dingding()
    print('第一次打开钉钉')
    time.sleep(13)
    d.close_dingding()
    print('第一次关闭钉钉')
    time.sleep(2)
    d.open_dingding()
    print('第二次打开钉钉，为了刷新现在是离线状态')
    time.sleep(5)

    print('重新登录钉钉中...')
    operation_list = [
        'adb shell input tap 550 1675', # 下一步 
        'adb shell input tap 700 2000'  # 同意并登录
    ]
    for operation in operation_list:
        process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
        process.wait()
        time.sleep(2)
    d.screencap("login_dingding")
    time.sleep(10)
    print('输入密码中...')
    operation_list = [
        'adb shell input tap 650 1700', # 密码登录
        'adb shell input tap 860 1986', 'adb shell input tap 286 1686', 'adb shell input tap 860 1986',
        'adb shell input tap 919 1693', 'adb shell input tap 405 1664', 'adb shell input tap 609 1684',
        'adb shell input tap 500 800'   # 登录
    ]
    for operation in operation_list:
        process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
        process.wait()
        time.sleep(1)
    time.sleep(10)
    d.screencap("dingding_home")

    d.send_email(False, 'login_dingding.png','dingding_home.png')
    d.close_dingding()

# 手动打卡，测试用，下班也生效的话，请在钉钉里设置下班也是极速打卡且每次打开钉钉会自动更新打卡
def manually_playCard():
    d = dingDing(directory)
    d.open_dingding()
    d.openplaycard_interface()
    d.click_playcard()
    d.send_email()
    d.close_dingding()

# BlockingScheduler
if __name__ == '__main__':
    args = sys.argv[1:]
    num = 3
    if len(args) == 1 and args[0].isdigit() and 1 <= int(args[0]) <= 8:
        num = int(args[0])
    print('开始执行策列：', num)
    # auto_playCard(num)
    # dingDing(directory).test_device()
    # relogin_dingding()
    # handling()
    manually_playCard()    