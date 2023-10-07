# DingDingAutoPlayCard

---

钉钉自动上下班打卡辅助
2023-09-13 更新

# 前提条件

* 公司电脑有Python环境
* 一台可以放在公司的安卓手机（如果你没有，抱歉，你可以不用再往下看了）
* 公司电脑需要安装ADB（本项目的根目录提供了windows下adb安装包）

# 电脑准备

1. 安装Python
2. 安装后，还需要安装依赖的python库:

   ```
   pip install flask
   pip install apsheduler
   pip install flask_script
   ```
3. 安装ADB

   1. windows版本adb下载地址:[https://adb.clockworkmod.com/](https://adb.clockworkmod.com/)
   2. 安装完成后，把adb.exe所在文件夹路径加入系统环境变量Path中

# 手机准备

## 使用

1. 确保手机开启USB调试模式
2. 执行playCard脚本即可

   ```python
   python playCard.py
   ```

### 手机需要打开开发者选项，通过USB数据线连接电脑(可通过wifi来连接手机用adb)。

### 打开CMD命令行，输入“adb devices”,能成功显示手机信息即可。

![cmdshow](https://github.com/1414044032/imgs/blob/master/adbcmd.png)

## 2.安装Python3.6

---

![pythonshow](https://github.com/1414044032/imgs/blob/master/python.png)

## 3.获取屏幕尺寸，设置模拟点击位置：

热心网友提供的简洁方式：可以打开"开发者设置"的输入找到"指针位置" 即可得到点击XY坐标轴。
---------------------------------------------------------------------------------------

![screen1](https://user-images.githubusercontent.com/40572216/64086339-31f6dc00-cd6a-11e9-9ccd-7ba0ba7624f1.png)
滑动解锁手机。如果手机屏幕自动点亮后不需要解锁。可以在文件中删除滑动解锁的部分。
--------------------------------------------------------------------------------
