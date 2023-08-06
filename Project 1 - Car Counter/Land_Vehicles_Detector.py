import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import cvzone
import numpy as np
from ultralytics import YOLO

cap = None  # Global variable to store the camera object
video_cap = None  # Global variable to store the video object

colors_dict = {}
vehicles_list = {
2: 'car',
3: 'motorcycle',
5: 'bus',
6: 'train',
7: 'truck'
}


def get_random_color(class_id):
    if class_id not in colors_dict:
        # Generate a random color with higher values for R, G, and B components
        min_value = 150  # Minimum value for R, G, and B components
        max_value = 255  # Maximum value for R, G, and B components
        color = tuple(np.random.randint(min_value, max_value, 3).tolist())
        colors_dict[class_id] = color
    return colors_dict[class_id]


def update_camerafeed():
    if cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            prediction_feed = model(frame)
            for predictions in prediction_feed:
                boxes = predictions.boxes
                for box in boxes:
                    if round(float(box.conf[0]), 2) > 0.4 and int(box.cls[0]) in list(vehicles_list.keys()):
                        xmin, ymin, xmax, ymax = map(int, box.xyxy[0])
                        w, h = xmax - xmin, ymax - ymin
                        color = get_random_color(int(box.cls[0]))
                        cvzone.cornerRect(frame, (xmin, ymin, w, h), colorC=color, colorR=(95, 69, 235), t=3, l=15)
                        conf = round(float(box.conf[0]), 2)
                        cvzone.putTextRect(frame, f"{conf}", pos=(max(0, xmin), max(30, ymin - 10)), scale=0.8, thickness=1, offset=3)
                        name_int = int(box.cls[0])
                        cvzone.putTextRect(frame, f"{model.names[name_int]}", pos=(max(0, xmin + 35), max(30, ymin - 10)),
                                           scale=0.8, thickness=1, offset=3)

            # Convert the frame to a format compatible with Tkinter's PhotoImage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

            # Update the canvas with the new frame
            canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            canvas.photo = photo  # Store a reference to avoid garbage collection issues

    window_2.after(15, update_camerafeed)  # Set the refresh rate (milliseconds)


video_window_active = False


def update_vidfeed():
    global video_cap, video_window_active
    if not video_window_active:
        return  # Return if the video window is not active

    confidence = float(conf_entry.get())
    if video_cap is not None and video_cap.isOpened():
        ret, frame = video_cap.read()
        if ret:
            prediction_feed = model(frame)
            for predictions in prediction_feed:
                boxes = predictions.boxes
                for box in boxes:
                    if float(box.conf[0]) > confidence and int(box.cls[0]) in list(vehicles_list.keys()):
                        xmin, ymin, xmax, ymax = map(int, box.xyxy[0])
                        w, h = xmax - xmin, ymax - ymin
                        color = get_random_color(int(box.cls[0]))
                        cvzone.cornerRect(frame, (xmin, ymin, w, h), colorC=color, colorR=(95, 69, 235), t=3, l=15)
                        conf = round(float(box.conf[0]), 2)
                        cvzone.putTextRect(frame, f"{conf}", pos=(max(0, xmin), max(30, ymin - 10)), scale=0.8, thickness=1, offset=3)
                        name_int = int(box.cls[0])
                        cvzone.putTextRect(frame, f"{model.names[name_int]}", pos=(max(0, xmin + 35), max(30, ymin - 10)),
                                           scale=0.8, thickness=1, offset=3)

            # Convert the frame to a format compatible with Tkinter's PhotoImage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

            # Update the label with the new frame
            label.config(image=photo)
            label.image = photo

    window_3.after(15, update_vidfeed)  # Set the refresh rate (milliseconds)

def exit_app():
    global cap, video_cap
    if cap is not None and cap.isOpened():
        cap.release()
    if video_cap is not None and video_cap.isOpened():
        video_cap.release()
    window_2.quit()


def run_vidurl():
    video_url = url_entry.get()
    conf_input = float(conf_entry.get())  # Get the confidence threshold as a string

    if not os.path.isfile(video_url):
        error_message.set("Invalid URL: Not a file.")
        window_3.update()
    else:
        error_message.set("")
        if (conf_input < 0) or (conf_input > 1):
            error_message.set("Confidence Invalid. Please enter a value between 0 and 1.")
            window_3.update()  # Update the window to display the error message immediately
            return  # Keeps recurring until if condition is not satisfied

        global video_cap
        if video_cap is not None and video_cap.isOpened():
            video_cap.release()
        video_cap = cv2.VideoCapture(video_url)
        update_vidfeed()


def window1to2():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        cap.set(3, 1080)  # Set the width to 1080
        cap.set(4, 720)  # Set the height to 720

    update_camerafeed()
    window_1.withdraw()  # Hide the main window
    window_2.deiconify()  # Show the camera feed window


def window2to1():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()
    window_2.withdraw()  # Hide the camera feed window
    window_1.deiconify()  # Show the main window


def window1to3():
    global video_window_active
    video_window_active = True
    window_1.withdraw()
    window_3.deiconify()


def window3to1():
    global video_window_active
    video_window_active = False
    window_3.withdraw()
    window_1.deiconify()

model = YOLO('yolov8n.pt')


window_1 = tk.Tk()
window_1.title("Video Feed Selection")
window_1.geometry("300x300")
choose_input_label = tk.Label(window_1, text="Choose your input", font=(13))
choose_input_label.grid(row=1, column=0, columnspan=2, padx=20, pady=20)
camera_button = tk.Button(window_1, text="Camera", command=window1to2, width=15, height=3)
camera_button.grid(row=0, column=0, padx=20, pady=20)

video_button = tk.Button(window_1, text="Video", command=window1to3, width=15, height=3)
video_button.grid(row=0, column=1, padx=20, pady=20)

window_2 = tk.Toplevel()  # Use Toplevel to create a secondary window
window_2.title("Camera Feed")
window_2.withdraw()  # Hide the camera feed window initially

canvas = tk.Canvas(window_2, width=1080, height=720)
canvas.grid(row=0, column=0, columnspan=2)

btn_exit = tk.Button(window_2, text="Exit", width=10, command=exit_app)
btn_exit.grid(row=1, column=1, padx=10, pady=5)

btn_return_window2 = tk.Button(window_2, text="Return", width=10, command=window2to1)
btn_return_window2.grid(row=1, column=0, padx=10, pady=5)

window_3 = tk.Toplevel()
window_3.title("Video Feed")
window_3.withdraw()

label = tk.Label(window_3)
label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

error_message = tk.StringVar()
error_message_label = tk.Label(window_3, textvariable=error_message, fg="red")
error_message_label.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

url_label = tk.Label(window_3, text="Video URL:")
url_label.grid(row=2, column=0, padx=10, pady=5)
url_entry = tk.Entry(window_3)
url_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

conf_label = tk.Label(window_3, text="Confidence Threshold:")
conf_label.grid(row=3, column=0, padx=10, pady=5)
conf_entry = tk.Entry(window_3)
conf_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

btn_runvid = tk.Button(window_3, text="Run Video Url", command=run_vidurl)
btn_runvid.grid(row=2, column=3, padx=10, pady=5, sticky="e")

btn_return_window3 = tk.Button(window_3, text="Return", width=10, command=window3to1)
btn_return_window3.grid(row=3, column=3, padx=10, pady=5, sticky="w")  # Update the column value to 3


window_1.mainloop()