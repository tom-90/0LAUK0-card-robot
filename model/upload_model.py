from dotenv import load_dotenv
load_dotenv()

from roboflow import Roboflow
import os


folder = input("Please enter run folder name to upload model for (e.g. train4): ")
train_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '../../runs/detect/' + folder))

rf = Roboflow(api_key=os.getenv("ROBOFLOW_API_KEY"))
project = rf.workspace(os.getenv("ROBOFLOW_WORKSPACE")).project(os.getenv("ROBOFLOW_PROJECT"))
project.version(int(os.getenv("ROBOFLOW_DATASET_VERSION"))).deploy(
    model_type="yolov8",
    model_path=train_path + "/"
)

