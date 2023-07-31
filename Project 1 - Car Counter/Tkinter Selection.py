import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os

cap = None  # Global variable to store the camera object

def update_camerafeed():
    if cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            canvas.photo = photo  # Store a reference to avoid garbage collection issues

    window_2.after(5, update_camerafeed)  # Set the refresh rate (milliseconds)


def update_vidfeed():
    if cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            label.config(image=img_tk)
            label.image = img_tk

    window_3.after(19, update_vidfeed)  # Set the refresh rate (milliseconds)


def exit_app():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()
    window_2.quit()


def run_vidurl():
    video_url = url_entry.get()
    if not os.path.isfile(video_url):
        error_message.set("Invalid URL: Not a file.")
    else:
        error_message.set("")
        global cap
        if cap is not None and cap.isOpened():
            cap.release()  # Release the camera if it's already opened

        cap = cv2.VideoCapture(video_url)
        update_vidfeed()


def window1to2():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        cap.set(3, 1080)  # Set the width to 1080
        cap.set(4, 720)  # Set the height to 720

    window_1.withdraw()  # Hide the main window
    window_2.deiconify()  # Show the camera feed window


def window2to1():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()
    window_2.withdraw()  # Hide the camera feed window
    window_1.deiconify()  # Show the main window


def window1to3():
    window_1.withdraw()
    window_3.deiconify()


def window3to1():
    window_3.withdraw()
    window_1.deiconify()

window_1 = tk.Tk()
window_1.title("Video Feed Selection")
camera_button = tk.Button(window_1, text="Camera", command=window1to2)
camera_button.pack()
video_button = tk.Button(window_1, text="Video", command=window1to3)
video_button.pack()

window_2 = tk.Toplevel()  # Use Toplevel to create a secondary window
window_2.title("Camera Feed")
window_2.withdraw()  # Hide the camera feed window initially

canvas = tk.Canvas(window_2, width=1080, height=720)
canvas.pack()

window_3 = tk.Toplevel()
window_3.title("Video Feed")
window_3.withdraw()
label = tk.Label(window_3)
label.pack()

error_message = tk.StringVar()
error_message_label = tk.Label(window_3, textvariable=error_message, fg="red")
error_message_label.pack()

btn_runvid = tk.Button(window_3, text="Run Video Url", command=run_vidurl)
btn_runvid.pack()
url_entry = tk.Entry(window_3, text="Input Video Url")
url_entry.pack()

btn_exit = tk.Button(window_2, text="Exit", width=10, command=exit_app)
btn_exit.pack(pady=5)

btn_exit = tk.Button(window_3, text="Exit", width=10, command=exit_app)
btn_exit.pack(pady=5)

btn_return = tk.Button(window_2, text="Return", width=10, command=window2to1)
btn_return.pack(pady=5)

btn_return = tk.Button(window_3, text="Return", width=10, command=window3to1)
btn_return.pack(pady=5)

update_camerafeed()

window_1.mainloop()