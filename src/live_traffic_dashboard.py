import cv2
import tkinter as tk
from PIL import Image, ImageTk

def start_live_dashboard(LANE_VIDEOS):

    root = tk.Toplevel()
    root.title("Live Traffic Dashboard")
    root.geometry("1200x700")
    root.configure(bg="#f4f6f9")

    tk.Label(
        root,
        text="Live Traffic Dashboard",
        font=("Arial", 18, "bold"),
        bg="#f4f6f9"
    ).pack(pady=10)

    container = tk.Frame(root, bg="#f4f6f9")
    container.pack(expand=True, fill="both")

    video_labels = {}
    caps = {}

    # ===============================
    # CREATE PANELS
    # ===============================
    for i, (lane, path) in enumerate(LANE_VIDEOS.items()):
        frame = tk.Frame(container, bg="white", bd=2, relief="groove")
        frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")

        tk.Label(frame, text=lane,
                 font=("Arial", 12, "bold"),
                 bg="white").pack(anchor="w", padx=10)

        lbl = tk.Label(frame, bg="black")
        lbl.pack(padx=10, pady=5)
        video_labels[lane] = lbl

        tk.Label(frame,
                 text="Density: -- | Ambulance: No | Time: --",
                 bg="white",
                 font=("Arial", 10)).pack()

        cap = cv2.VideoCapture(path)
        if cap.isOpened():
            caps[lane] = cap
        else:
            print(f"❌ Cannot open video for {lane}")

    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)

    # ===============================
    # UPDATE FRAMES
    # ===============================
    def update_frames():
        for lane, cap in caps.items():
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    continue

            frame = cv2.resize(frame, (520, 280))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(img)

            video_labels[lane].imgtk = imgtk
            video_labels[lane].configure(image=imgtk)

        root.after(30, update_frames)

    update_frames()
