#!/bin/bash
cd "$(dirname "$0")"
export $(grep -v '^#' ../.env | xargs)

yolo task=detect mode=train model=./base/yolov8s.pt data=./datasets/v$ROBOFLOW_DATASET_VERSION/data.yaml epochs=250 imgsz=1024 batch=4 plots=True