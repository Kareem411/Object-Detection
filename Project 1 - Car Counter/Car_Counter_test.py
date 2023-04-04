from ultralytics import YOLO
import cv2
import cvzone

model = YOLO('../Yolo-weights/yolov8n.pt')
user_input = input("Camera or Video feed? (c/v)\n")
if user_input not in ["c", "v"]:
    print("Invalid input, please enter 'c' or 'v'")
    exit()

if user_input == "c":
    cap = cv2.VideoCapture(2)
    cap.set(3, 1080)
    cap.set(4, 720)
elif user_input == "v":
    video_url = input("Video url: \n")
    cap = cv2.VideoCapture(video_url)
    cap.set(3, 1080)
    cap.set(4, 720)

answer = input("Check for a name? (y/n)\n").lower() == "y"
if answer:
    check = input('What to check for? (separate by comma)\n').replace(" ", "").lower().split(",")

mask_answer = input("Use a mask? (y/n)\n").lower() == "y"
if mask_answer:
    mask_url = str(input("Mask URL: \n"))
    mask = cv2.imread(mask_url)

while True:
    _, feed = cap.read()
    if mask_answer:
        masked_feed = cv2.bitwise_and(feed, mask)
        prediction_feed = model(masked_feed, stream=True)
    else:
        prediction_feed = model(feed, stream=True)

    for predictions in prediction_feed:
        boxes = predictions.boxes
        for box in boxes:
            xmin, ymin, xmax, ymax = map(int, box.xyxy[0])
            w, h = xmax - xmin, ymax - ymin

            if answer:
                if model.names[int(box.cls[0])] in check:
                    cvzone.cornerRect(feed, (xmin, ymin, w, h), colorC=(153, 52, 43), colorR=(95, 69, 235), t=3, l=15)
                    conf = round(float(box.conf[0]), 2)
                    cvzone.putTextRect(feed, f"{conf}", pos=(max(0, xmin), max(30, ymin - 10)), scale=0.8, thickness=1, offset=3)
                    cvzone.putTextRect(feed, f"{model.names[int(box.cls[0])]}", pos=(max(0, xmin + 35), max(30, ymin - 10)), scale=0.8,
                                       thickness=1, offset=3)
            else:
                cvzone.cornerRect(feed, (xmin, ymin, w, h), colorC=(153, 52, 43), colorR=(95, 69, 235), t=3, l=15)
                conf = round(float(box.conf[0]), 2)
                cvzone.putTextRect(feed, f"{conf}", pos=(max(0, xmin), max(30, ymin - 10)), scale=0.8, thickness=1,
                                   offset=3)
                name_int = int(box.cls[0])
                cvzone.putTextRect(feed, f"{model.names[name_int]}", pos=(max(0, xmin + 35), max(30, ymin - 10)), scale=0.8,
                                   thickness=1, offset=3)

    cv2.imshow("camera", feed)
    cv2.waitKey(1)
