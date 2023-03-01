#!/bin/bash
cd "$(dirname "$0")"
export $(grep -v '^#' ../.env | xargs)

tensorboard --logdir ../runs/detect/train2 --host 0.0.0.0