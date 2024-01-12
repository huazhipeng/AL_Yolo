import os
import platform
from pathlib import Path
# from mouse_control import set_global_var
import torch
from models.common import DetectMultiBackend
from utils.general import (LOGGER, Profile, check_img_size, check_requirements, cv2, non_max_suppression, scale_boxes, strip_optimizer)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device
import time
from Capture import LoadScreen
from mouse_control import move_to

ROOT = os.getcwd()


class YOLOv5Detector:
    def __init__(
        self,
        weights='',
        data='',
        imgsz=(640, 640),
        conf_thres=0.25,
        iou_thres=0.45,
        max_det=1000,
        device=0,
        view_img=False, #changed
        classes=None,
        agnostic_nms=False,
        augment=False,
        # update=False,
        line_thickness=3,
        hide_labels=False,
        hide_conf=False,
        half=True,
        dnn=False
    ):
        self.weights = weights
        self.data = data
        self.imgsz = imgsz
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.max_det = max_det
        self.device = device
        self.view_img = view_img
        self.classes = classes
        self.agnostic_nms = agnostic_nms
        self.augment = augment
        # self.update = update
        self.line_thickness = line_thickness
        self.hide_labels = hide_labels
        self.hide_conf = hide_conf
        self.half = half
        self.dnn = dnn
        self.should_stop = False  # flag to stop
        self.is_enable_mouse_lock = False

    @staticmethod
    def run(self):
        print(self.weights, self.data)
        # Load model
        device = select_device(0)
        model = DetectMultiBackend(self.weights, device=device, dnn=self.dnn, data=self.data, fp16=self.half)
        stride, names, pt = model.stride, model.names, model.pt
        imgsz = self.imgsz
        # imgsz = check_img_size(imgsz, s=stride)  # check image size

        # Dataloader
        bs = 1  # batch_size
        
        dataset = LoadScreen(stride=stride, auto=pt)

        # Run inference
        model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
        dt = (Profile(), Profile(), Profile())
        
        frame_cnt = 0
        that_time = 0
        
        for path, im, im0s, vid_cap, s in dataset:
            with dt[0]:
                im = torch.from_numpy(im).to(model.device)
                im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
                im /= 255  # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim

            # Inference
            with dt[1]:
                pred = model(im, augment=self.augment, visualize=False)

            # NMS
            with dt[2]:
                pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms, max_det=self.max_det)
            
            # Quit
            if self.should_stop:
                cv2.destroyAllWindows()
                break
            
            # Process predictions
            for i, det in enumerate(pred):  # per image
                
                #quit
                if self.should_stop:
                    cv2.destroyAllWindows()
                    break
                
                
                p, im0 = path, im0s.copy()

                p = Path(p)  # to Path
                s += '%gx%g ' % im.shape[2:]  # print string
                annotator = Annotator(im0, line_width=self.line_thickness, example=str(names))
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, 5].unique():
                        n = (det[:, 5] == c).sum()  # detections per class
                        s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
            
                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)  # integer class
                        label = None if self.hide_labels else (names[c] if self.hide_conf else f'{names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))

                        # print(xyxy)
                        print("target detected")
                        if self.is_enable_mouse_lock:
                            move_to(xyxy) # mouse control
                        
                # Stream results
                im0 = annotator.result()
                now_time = time.time()
                frame_cnt += 1
                duration_time = now_time - that_time
                fps = frame_cnt / duration_time
                if frame_cnt >= 50:
                    that_time = now_time
                    frame_cnt = 0
                if self.view_img:
                    # FPS show
                    cv2.setWindowTitle(str(p),str(fps))
                    
                    time_1 = time.time()
                    cv2.imshow(str(p), im0)
                    cv2.waitKey(1)
                    time_2 = time.time()
                    print("imgShow takes {:.2f} ms".format((time_2-time_1)*1E3))
                else:
                    print("Fps is ", fps)

        # if self.update:
        #     strip_optimizer(self.weights[0])  # update model (to fix SourceChangeWarning)

        
    def work(self):
        check_requirements(exclude=('tensorboard', 'thop'))
        self.run(self)
        
    def stop(self):
        self.should_stop = True
    
    def start_mouse(self):
        self.is_enable_mouse_lock = True

    def stop_mouse(self):
        self.is_enable_mouse_lock = False
