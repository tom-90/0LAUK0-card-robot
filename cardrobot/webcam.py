from ultralytics.yolo.data.dataloaders.stream_loaders import LoadStreams, SourceTypes
import torch
import cv2
import math
import numpy as np
from threading import Thread
from ultralytics.yolo.data.augment import LetterBox

# Largely copied from Ultralytics YOLOv8 source code
# Only added the ability to provide a resolution parameter

class WebcamSource(LoadStreams):
    def __init__(self, source, resolution, predictor):
        torch.backends.cudnn.benchmark = True

        self.mode = 'stream'
        self.imgsz = predictor.args.imgsz
        self.stride = 32
        self.vid_stride = predictor.args.vid_stride
        self.source_type = SourceTypes(webcam=True)

        self.sources = [source]
        source = eval(source) if source.isnumeric() else source
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise ConnectionError(f'Failed to open {source}')

        if resolution != None:
            res = resolution.split('x')
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(res[0]))
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(res[1]))

        fps = cap.get(cv2.CAP_PROP_FPS)  # warning: may return 0 or nan
        self.frames = [max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')]  # infinite stream fallback
        self.fps = [max((fps if math.isfinite(fps) else 0) % 100, 0) or 30]  # 30 FPS fallback

        self.imgs = [None]
        success, self.imgs[0] = cap.read()  # guarantee first frame
        if not success or self.imgs[0] is None:
            raise ConnectionError(f'Failed to read images from {source}')

        self.threads = [Thread(target=self.update, args=([0, cap, source]), daemon=True)]
        self.threads[0].start()

        # check for common shapes
        s = np.stack([LetterBox(self.imgsz, True, stride=self.stride)(image=x).shape for x in self.imgs])
        self.rect = np.unique(s, axis=0).shape[0] == 1  # rect inference if all shapes equal
        self.auto = self.rect
        self.transforms = None
        self.bs = self.__len__()