import subprocess
import time
import setting
import datetime
import smtplib
import os
import time

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
        operation_list1 = [self.adbselect_work, self.adbselect_playcard]
        for operation in operation_list1:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            # 等待点击屏幕后响应
            time.sleep(5)
        # 等待工作页面加载
        time.sleep(20)
        
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
        # 设备截屏保存到sdcard
        self.adbscreencap = 'adb shell screencap -p sdcard/screen.png'
        # 传送到计算机
        self.adbpull = 'adb pull sdcard/screen.png %s' % (screen_dir)
        # 删除设备截屏
        self.adbrm_screencap = 'adb shell rm -r sdcard/screen.png'

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

    # 2 打开打卡界面
    def openplaycard_interface(self):
        print("打开打卡界面中...")
        operation_list = [self.adbselect_work, self.adbselect_playcard]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
        time.sleep(20)
        print("成功打开打卡界面")

    # 3 截屏>> 发送到电脑 >> 删除手机中保存的截屏
    def screencap(self):
        print("截屏, 发送至电脑中...")
        operation_list = [self.adbscreencap, self.adbpull, self.adbrm_screencap]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False, stdout=subprocess.PIPE)
            process.wait()
        print("成功发送至电脑")

    # 4 发送邮件（QQ邮箱）
    @staticmethod
    def send_email():
        """
        qq邮箱 需要先登录网页版，开启SMTP服务。获取授权码，
        :return:
        """
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        message = MIMEMultipart('related')
        subject = now_time + '打卡'
        message['Subject'] = subject
        # message['From'] = "日常打卡"
        message['From'] = sender
        message['To'] = receive
        content = MIMEText('<html><body><img src="cid:imageid" alt="imageid"></body></html>', 'html', 'utf-8')
        message.attach(content)
        file = open(os.path.join(screen_dir, "screen.png"), "rb")
        img_data = file.read()
        file.close()
        img = MIMEImage(img_data)
        img.add_header('Content-ID', 'imageid')
        message.attach(img)
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

    # 上班(极速打卡)
    @with_open_close_dingding
    def goto_work(self):
        self.screencap()
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
        self.screencap()
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
        # [四]22:00
        trigger = CronTrigger(day_of_week='mon,tue', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='thu', hour=22, minute=0, jitter=120)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 5:
        # [二三]21:00
        # [四]22:30
        trigger = CronTrigger(day_of_week='tue,wed', hour=21, minute=0, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='thu', hour=22, minute=30, jitter=120)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 6:
        # [二四]21:30
        trigger = CronTrigger(day_of_week='tue,thu', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    elif num == 7:
        # [三]22:00
        # [四]21:00
        trigger = CronTrigger(day_of_week='wed', hour=22, minute=00, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
        trigger = CronTrigger(day_of_week='thu', hour=21, minute=00, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)
    else:
        trigger = CronTrigger(day_of_week='tue', hour=21, minute=30, jitter=180)
        scheduler.add_job(dingDing(directory).off_work, trigger=trigger)

    scheduler.start()

# 手动打卡，测试用，下班也生效的话，请在钉钉里设置下班也是极速打卡且每次打开钉钉会自动更新打卡
def manually_playCard():
    d = dingDing(directory)
    d.open_dingding()
    d.openplaycard_interface()
    #d.click_playcard()
    d.screencap()
    d.send_email()
    d.close_dingding()

# BlockingScheduler
if __name__ == '__main__':

    print('开始执行')
    auto_playCard(4)
    #manually_playCard()