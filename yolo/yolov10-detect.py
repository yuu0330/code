import cv2
import supervision as sv
from ultralytics import YOLO
model = YOLO(f'runs/detect/train5/weights/best.pt')
bounding_box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()  
cap=cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
if not cap.isOpened():
    print("can't open the webcam")
while True:
    ret,frame=cap.read()  
    if not ret:
        break
    results = model(frame, conf=0.15)[0]
    detections = sv.Detections.from_ultralytics(results)
    annotated_image = bounding_box_annotator.annotate(
    scene=frame, detections=detections)
    annotated_image = label_annotator.annotate(
    scene=annotated_image, detections=detections)
    cv2.imshow('Webcam',annotated_image)
    k=cv2.waitKey(1)
    if k%256==27:
        print("Escape hit,closing...")
        break   
cap.release()
cv2.destroyAllWindows()
