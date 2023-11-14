# -*- coding: utf-8 -*-
from detect import YOLOv5Detector
import pynput
import winsound
import mouse_control
import tkinter as tk
import threading


detector = YOLOv5Detector(
    weights='best.pt',
    data='AL_data.yaml',
    imgsz=(640, 640),
    conf_thres=0.45,
    iou_thres=0.4,
    device='cuda'
)

is_initiate = False
is_start = False

def enable_button(button):
    button.config(state=tk.NORMAL)


def initiate():
    global is_initiate
    if not is_initiate:
        detector_thread = threading.Thread(target=detector.work)
        detector_thread.start()
        is_initiate = True
        initiate_button.config(state=tk.DISABLED)
        root.after(1000, lambda: enable_button(initiate_button))
        print("目标检测已开启")

def end():
    global is_initiate
    if is_initiate:
        detector.stop()
        is_initiate = False
        end_button.config(state=tk.DISABLED)
        root.after(1000, lambda: enable_button(end_button))
        print("目标检测已停止")

def start():
    global is_start
    if not is_start:
        winsound.Beep(400, 200)
        mouse_control.run()
        is_start = True
        start_button.config(state=tk.DISABLED)
        root.after(1000, lambda: enable_button(start_button))
        print("鼠标锁定已开启")
        
def stop():
    global is_start
    if is_start:
        winsound.Beep(600, 200)
        mouse_control.stop()
        is_start = False
        stop_button.config(state=tk.DISABLED)
        root.after(1000, lambda: enable_button(stop_button))
        print("鼠标锁定已关闭")

def release():
    global is_start, is_initiate
    if is_start:
        mouse_control.stop()
        is_start = False
    if is_initiate:
        detector.stop()
        is_initiate = False
    root.destroy()
    print("关闭程序")

if __name__ == '__main__':
    root = tk.Tk()
    root.title("AL_Yolo")
    root.geometry("300x200")
    initiate_button = tk.Button(root, text="开启目标检测", command=initiate)
    initiate_button.grid(row=0, column=0)
    end_button = tk.Button(root, text="停止目标检测", command=end)
    end_button.grid(row=1, column=0)
    start_button = tk.Button(root, text="开启鼠标锁定", command=start)
    start_button.grid(row=0, column=1)
    stop_button = tk.Button(root, text="暂停鼠标锁定", command=stop)
    stop_button.grid(row=1, column=1)

    release_button = tk.Button(root, text="退出", command=release)
    release_button.grid(row=0, column=2)
    
    root.mainloop()
