from dotenv import load_dotenv
load_dotenv()

from roboflow import Roboflow
import os
import yaml

dataset_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '../datasets/v' + os.getenv("ROBOFLOW_DATASET_VERSION")))

rf = Roboflow(api_key=os.getenv("ROBOFLOW_API_KEY"))
project = rf.workspace(os.getenv("ROBOFLOW_WORKSPACE")).project(os.getenv("ROBOFLOW_PROJECT"))
dataset = project.version(int(os.getenv("ROBOFLOW_DATASET_VERSION"))).download(
    "yolov8",
    location=dataset_path
)

# Modify train, test and val paths to be absolute to avoid errors
data = None
with open(os.path.join(dataset_path, 'data.yaml'), 'r') as stream:
    data = yaml.safe_load(stream)

    data['train'] = os.path.join(dataset_path, data['train'])
    data['test'] = os.path.join(dataset_path, data['test'])
    data['val'] = os.path.join(dataset_path, data['val'])

with open(os.path.join(dataset_path, 'data.yaml'), 'w') as stream:
    yaml.dump(data, stream)