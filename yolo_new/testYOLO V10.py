from ultralytics import YOLO
# Load a model
model = YOLO('yolov10x.pt')

results = model.predict('data/images')
results[0].show()