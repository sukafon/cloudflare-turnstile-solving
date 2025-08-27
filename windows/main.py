import cv2
import numpy as np
from mss import mss
import pyautogui
import time
from datetime import datetime
import random
import math


# --- 函数定义部分---
def match_template(img, template, offset=(0, 0), threshold=0.7):
    """在 img 中匹配 template，返回偏移后的屏幕坐标"""
    # 如果模板或图像为空，则直接返回
    if (
        template is None
        or img is None
        or template.shape[0] == 0
        or template.shape[1] == 0
    ):
        return None, (0, 0)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = template_gray.shape[::-1]

    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val < threshold:
        return None, (w, h)

    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str}] 尝试匹配... 匹配度 {max_val:.2f}")

    top_left = max_loc
    screen_coord = (top_left[0] + offset[0], top_left[1] + offset[1])
    return screen_coord, (w, h)


def move_mouse(x, y):
    """移动鼠标到指定坐标"""
    # 水平方向和竖直方向偏移
    offset_x = random.randint(-50, 50)
    offset_y = random.randint(-5, 5)
    pyautogui.moveTo(x + offset_x, y + offset_y)


def click_mouse():
    """模拟鼠标左键点击"""
    pyautogui.mouseDown(button="left")  # 按下左键
    time.sleep(0.2)  # 等待 0.2 秒
    pyautogui.mouseUp(button="left")  # 松开左键


def move_mouse_around(
    x_center,
    y_center,
    radius_min=20,
    radius_max=50,
    steps=12,
    delay_min=0.01,
    delay_max=0.05,
):
    """
    模拟真实鼠标围绕移动
    x_center, y_center: 中心点
    radius_min, radius_max: 幅度范围
    steps: 移动点数
    delay_min, delay_max: 每步延迟随机化
    """
    radius = random.randint(radius_min, radius_max)
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        # 计算偏移
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        x = x_center + int(radius * math.cos(angle)) + offset_x
        y = y_center + int(radius * math.sin(angle)) + offset_y
        move_mouse(x, y)  # 移动鼠标
        time.sleep(random.uniform(delay_min, delay_max))


# --- 初始化部分 ---
sct = mss()
monitor = sct.monitors[0]

# 模板加载
try:
    template = cv2.imread("./template/template.png")
    sub_template = cv2.imread("./template/sub_template.png")
    if template is None or sub_template is None:
        raise FileNotFoundError
except FileNotFoundError:
    print("错误：无法加载模板文件，请检查路径！")
    exit()

# --- 优化逻辑变量 ---
cached_search_region = None  # 用于缓存搜索区域的字典
rescan_counter = 0  # 周期性重扫计数器
RESCAN_INTERVAL = 30  # 每30次区域搜索后，强制进行一次全屏扫描
PADDING = 30  # 在找到的区域周围增加30像素的内边距，以提高鲁棒性
interval_time = 5  # 扫描间隔时间

now = datetime.now()
time_str = now.strftime("%Y-%m-%d %H:%M:%S")
print(f"[{time_str}] 自动点击验证码程序已启动")
# --- 主循环部分 ---
while True:
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # 1. 决定是全屏搜索还是区域搜索
    if cached_search_region is None or rescan_counter >= RESCAN_INTERVAL:
        # if rescan_counter >= RESCAN_INTERVAL:
        #     print(f"[{time_str}] 达到重扫周期，执行全屏扫描以校准位置")
        # else:
        #     print(f"[{time_str}] 未找到缓存区域，执行全屏扫描")

        rescan_counter = 0  # 重置计数器

        # --- 全屏扫描逻辑 ---
        full_screenshot = np.array(sct.grab(monitor))
        overall_coord, (W, H) = match_template(full_screenshot, template)

        if overall_coord is None:
            # print(f"[{time_str}] 全屏扫描未匹配到模板区域")
            time.sleep(interval_time)
            continue

        # 成功找到，计算并缓存下一次的搜索区域
        x0, y0 = overall_coord
        cached_search_region = {
            "top": max(0, y0 - PADDING),
            "left": max(0, x0 - PADDING),
            "width": W + 2 * PADDING,
            "height": H + 2 * PADDING,
        }
        print(f"[{time_str}] 已定位并缓存搜索区域: {cached_search_region}")

        # 在本次的全屏截图中继续查找子元素
        sub_img = full_screenshot[y0 : y0 + H, x0 : x0 + W]
        element_coord, (w, h) = match_template(
            sub_img, sub_template, offset=overall_coord
        )

    else:
        # --- 区域扫描逻辑 ---
        rescan_counter += 1
        # print(f"[{time_str}] 使用缓存区域进行扫描 (周期: {rescan_counter}/{RESCAN_INTERVAL})")

        region_screenshot = np.array(sct.grab(cached_search_region))

        # offset 必须是缓存区域的左上角坐标
        offset = (cached_search_region["left"], cached_search_region["top"])
        element_coord, (w, h) = match_template(
            region_screenshot, sub_template, offset=offset
        )

        # 缓存区域内未找到验证码
        if element_coord is None:
            # cached_search_region = None # 清空缓存
            time.sleep(interval_time)  # 间隔多少秒循环检测
            continue

    # --- 后续操作 ---
    if element_coord is None:
        print(
            f"[{time_str}] 没有匹配到子元素，请更新图片模板"
        )  # 这不正常，可能需要更新图片模板
        time.sleep(interval_time * 2)
        continue

    print(f"[{time_str}] 检测到目标！元素屏幕坐标：{element_coord}")

    # 待点击的元素中心坐标
    x = element_coord[0] + w // 2
    y = element_coord[1] + h // 2

    # 先绕一圈
    move_mouse_around(x, y)
    # 移动到目标区域
    move_mouse(x, y)
    time.sleep(0.3)  # 延迟一会
    # 点击验证
    click_mouse()

    print(f"[{time_str}] 已完成点击")
    time.sleep(interval_time)  # 间隔多少秒循环检测
