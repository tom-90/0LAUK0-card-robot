from dotenv import load_dotenv
load_dotenv()

from ultralytics.yolo.v8 import detect
import os

def predict():
    predictor = detect.DetectionPredictor(overrides={
        'show': True,
        'save': False,
        'verbose': False,
        'source': os.getenv('WEBCAM_SOURCE'),
        'model': os.path.abspath(os.path.join(os.path.realpath(__file__), '../../model/best_weights.pt'))
    })

    # The predictor function will keep predicting and returning values as we go
    for data in predictor(stream=True):
        # data contains all predictions made in the current frame/image from the webcam

        data = data.to("cpu") # Move data to CPU

        # Print the bounding boxes and their classes
        for boxIndex, box in enumerate(data.boxes):
            print(f'Box {boxIndex}: {box.xyxy.numpy()}')
            for predIndex, cls in enumerate(box.cls):
                clsName = data.names[int(cls)]
                print(f' - Class: {clsName} (conf={box.conf[predIndex]})')

        if(len(data.boxes) > 0):
            print('\n')

predict()