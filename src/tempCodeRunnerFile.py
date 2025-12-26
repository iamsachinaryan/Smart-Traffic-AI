import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import traceback
import datetime

# --- CUSTOM MODULES ---
from detect import TrafficDetector
from logic import TrafficManager
from database import TrafficDB
from prediction import Predictor
import config

# ==========================================
# 1. ADMIN LOGIN SYSTEM (NEW)
# ==========================================
class AdminLogin:
    def __init__(self):
        self.is_logged_in = False
        self.root = tk.Tk()
        self.root.title("Traffic Control - Secure Login")
        self.root.geometry("400x450")
        self.root.configure(bg="#121212") # Dark Theme
        self.root.resizable(False, False)

        # Icon/Logo Placeholder
        tk.Label(self.root, text="🔐", font=("Arial", 60), bg="#121212", fg="#00cec9").pack(pady=(40, 10))
        tk.Label(self.root, text="ADMIN ACCESS", font=("Segoe UI", 18, "bold"), bg="#121212", fg="white").pack(pady=10)

        # Username
        tk.Label(self.root, text="Username", bg="#121212", fg="gray", font=("Arial", 10)).pack(anchor="w", padx=50)
        self.user_entry = tk.Entry(self.root, font=("Arial", 12), bg="#2d3436", fg="white", insertbackground="white", bd=0)
        self.user_entry.pack(fill="x", padx=50, pady=5, ipady=5)

        # Password
        tk.Label(self.root, text="Password", bg="#121212", fg="gray", font=("Arial", 10)).pack(anchor="w", padx=50, pady=(15, 0))
        self.pass_entry = tk.Entry(self.root, font=("Arial", 12), bg="#2d3436", fg="white", insertbackground="white", bd=0, show="*")
        self.pass_entry.pack(fill="x", padx=50, pady=5, ipady=5)

        # Login Button
        tk.Button(self.root, text="LOGIN", command=self.verify, bg="#0984e3", fg="white", font=("Arial", 12, "bold"), bd=0, width=15).pack(pady=30)
        
        # Footer
        tk.Label(self.root, text="Smart Traffic Management System v3.0", bg="#121212", fg="#636e72", font=("Arial", 8)).pack(side="bottom", pady=10)

        self.root.mainloop()

    def verify(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        # --- HARDCODED CREDENTIALS ---
        if username == "admin" and password == "admin123":
            messagebox.showinfo("Success", "Welcome, Admin! Access Granted.")
            self.is_logged_in = True
            self.root.destroy() # Close login, open next screen
        else:
            messagebox.showerror("Access Denied", "Invalid Username or Password!")

# ==========================================
# 2. SETUP DASHBOARD (LAUNCHER)
# ==========================================
class VideoLauncher:
    def __init__(self):
        self.video_paths = {}
        self.root = tk.Tk()
        self.root.title("Control Room Dashboard")
        self.root.geometry("600x550")
        self.root.configure(bg="#1e1e1e")

        tk.Label(self.root, text="🚦 System Configuration", font=("Segoe UI", 20, "bold"), bg="#1e1e1e", fg="#00cec9").pack(pady=20)
        tk.Label(self.root, text="Configure live feeds for the junction.", font=("Arial", 10), bg="#1e1e1e", fg="#a0a0a0").pack()

        self.btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.btn_frame.pack(pady=20)
        self.path_labels = {}
        self.directions = ['North', 'South', 'East', 'West']
        
        for d in self.directions:
            frame = tk.Frame(self.btn_frame, bg="#1e1e1e")
            frame.pack(fill="x", pady=8, padx=40)
            tk.Label(frame, text=f"{d}:", font=("Arial", 12, "bold"), bg="#1e1e1e", fg="white", width=6, anchor="w").pack(side="left")
            btn = tk.Button(frame, text="Browse", command=lambda x=d: self.select_file(x), bg="#333", fg="white", width=10)
            btn.pack(side="left", padx=10)
            lbl = tk.Label(frame, text="-- No Video --", bg="#1e1e1e", fg="#ff4757", font=("Arial", 9))
            lbl.pack(side="left")
            self.path_labels[d] = lbl

        tk.Button(self.root, text="INITIALIZE SYSTEM", command=self.start_sys, bg="#2ed573", fg="white", font=("Arial", 14, "bold"), width=25).pack(pady=40)
        
        self.ready = False
        self.root.mainloop()

    def select_file(self, direction):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
        if path:
            self.video_paths[direction] = path
            filename = os.path.basename(path)
            if len(filename) > 25: filename = filename[:22] + "..."
            self.path_labels[direction].config(text=filename, fg="#2ed573")

    def start_sys(self):
        if not self.video_paths:
            messagebox.showerror("Wait!", "Please select at least 1 video.")
            return
        self.ready = True
        self.root.destroy()

# ==========================================
# 3. UI DRAWING (Phase 3 Visuals)
# ==========================================
def draw_ui(video_frame, name, is_green, rem_time, load, amb, breakdown):
    vid_h, vid_w, _ = video_frame.shape
    sidebar_w = 110  
    total_w = vid_w + sidebar_w
    
    canvas = np.full((vid_h, total_w, 3), (30, 30, 30), dtype=np.uint8) 
    
    # --- LIGHTS ---
    cx = sidebar_w // 2
    c_off = (50, 50, 50) 
    c_red = (0, 0, 255) if not is_green else c_off
    c_grn = (0, 255, 0) if is_green else c_off
    
    cv2.circle(canvas, (cx, 40), 20, c_red, -1)
    cv2.circle(canvas, (cx, 40), 20, (0,0,0), 2)
    cv2.circle(canvas, (cx, 90), 20, c_off, -1)
    cv2.circle(canvas, (cx, 90), 20, (0,0,0), 2)
    cv2.circle(canvas, (cx, 140), 20, c_grn, -1)
    cv2.circle(canvas, (cx, 140), 20, (0,0,0), 2)

    # --- STATS ---
    y_stats = 190
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.line(canvas, (10, 175), (sidebar_w-10, 175), (100,100,100), 1)
    
    cv2.putText(canvas, "VEHICLES", (15, y_stats), font, 0.5, (0, 255, 255), 1)
    cv2.putText(canvas, f"Car : {breakdown['car']}", (15, y_stats + 25), font, 0.5, (200, 200, 200), 1)
    cv2.putText(canvas, f"Bike: {breakdown['bike']}", (15, y_stats + 50), font, 0.5, (200, 200, 200), 1)
    cv2.putText(canvas, f"Hvy : {breakdown['heavy']}", (15, y_stats + 75), font, 0.5, (200, 200, 200), 1)
    
    cv2.putText(canvas, f"DENSITY", (15, y_stats + 110), font, 0.5, (0, 255, 255), 1)
    
    # High Density Alert
    if load > 50:
        cv2.putText(canvas, f"{load}", (30, y_stats + 140), font, 1.0, (0, 0, 255), 3)
        cv2.putText(canvas, "JAM!", (35, y_stats + 170), font, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(canvas, f"{load}", (30, y_stats + 140), font, 1.0, (0, 255, 0), 2)

    canvas[:, sidebar_w:] = video_frame
    
    # Bottom Status
    overlay = canvas.copy()
    cv2.rectangle(overlay, (sidebar_w, vid_h - 40), (total_w, vid_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, canvas, 0.3, 0, canvas)
    
    time_str = f"{rem_time}s" if rem_time > 0 else "--"
    amb_txt = "DETECTED!" if amb else "No"
    amb_col = (0, 0, 255) if amb else (180, 180, 180)
    
    cv2.putText(canvas, f"Timer: {time_str}", (sidebar_w + 20, vid_h - 12), font, 0.7, (255, 255, 255), 2)
    cv2.putText(canvas, f"Amb: {amb_txt}", (sidebar_w + 180, vid_h - 12), font, 0.6, amb_col, 2)
    cv2.putText(canvas, name, (total_w - 120, 30), font, 0.8, (255, 255, 255), 2)

    return canvas

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    try:
        # STEP 1: LOGIN
        login_screen = AdminLogin()
        
        # Only proceed if login was successful
        if login_screen.is_logged_in:
            
            # STEP 2: DASHBOARD SETUP
            launcher = VideoLauncher()
            
            if launcher.ready:
                print("🚀 Access Granted. Initializing AI Core...")
                
                # Check Evidence Folder
                if not os.path.exists("evidence"): os.makedirs("evidence")

                # Init Modules
                db = TrafficDB()
                pred = Predictor(db)
                brain = TrafficManager(pred)
                detector = TrafficDetector()
                
                caps = {d: cv2.VideoCapture(p) for d, p in launcher.video_paths.items()}
                pair_ns = ['North', 'South']
                pair_ew = ['East', 'West']
                active_pair = 'NS'
                timer_end = time.time() + 5
                reason = "System Start"
                
                frame_counter = 0
                SKIP_FRAMES = 2
                
                default_breakdown = {'car': 0, 'bike': 0, 'heavy': 0, 'rickshaw': 0}
                last_data = {d: {'load': 0, 'ambulance': False, 'breakdown': default_breakdown} for d in caps}
                last_visuals = {}
                last_snapshot_time = 0
                VID_W, VID_H = 600, 360 

                print("✅ Live Monitoring Started...")

                while True:
                    frame_counter += 1
                    current_data = {}
                    display_frames_map = {}
                    any_ambulance_now = False

                    # SENSING
                    for d, cap in caps.items():
                        ret, frame = cap.read()
                        if not ret:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            ret, frame = cap.read()
                            if not ret: frame = np.zeros((VID_H, VID_W, 3), dtype=np.uint8)
                        
                        frame = cv2.resize(frame, (VID_W, VID_H))
                        
                        if frame_counter % (SKIP_FRAMES + 1) == 0:
                            processed_frame, breakdown, load, is_amb = detector.analyze_frame(frame)
                            last_data[d] = {'load': load, 'ambulance': is_amb, 'breakdown': breakdown}
                            last_visuals[d] = processed_frame
                            if is_amb: any_ambulance_now = True
                        
                        current_data[d] = last_data[d]
                        display_frames_map[d] = last_visuals.get(d, frame).copy()

                    # LOGIC
                    rem_time = int(timer_end - time.time())
                    if rem_time <= 0:
                        rem_time = 0
                        decision = brain.decide_phase(current_data)
                        active_pair = decision['active_pair']
                        timer_end = time.time() + decision['time']
                        reason = decision['reason']
                        if active_pair != "ALL_RED":
                            db.log_signal(active_pair, 0, 0, decision['time'], False)
                        print(f"🔄 Switch: {active_pair} -> {reason}")

                    # DISPLAY
                    final_panels = []
                    for d in ['North', 'South', 'East', 'West']:
                        if d in display_frames_map:
                            src_frame = display_frames_map[d]
                            is_green = False
                            if active_pair == 'NS' and d in pair_ns: is_green = True
                            elif active_pair == 'EW' and d in pair_ew: is_green = True
                            panel = draw_ui(src_frame, d, is_green, rem_time, last_data[d]['load'], last_data[d]['ambulance'], last_data[d]['breakdown'])
                        else:
                            empty_vid = np.zeros((VID_H, VID_W, 3), dtype=np.uint8)
                            panel = draw_ui(empty_vid, d, False, 0, 0, False, default_breakdown)
                        final_panels.append(panel)

                    top = np.hstack((final_panels[0], final_panels[1]))
                    bot = np.hstack((final_panels[2], final_panels[3]))
                    dashboard = np.vstack((top, bot))

                    h, w, _ = dashboard.shape
                    header = np.zeros((60, w, 3), dtype=np.uint8)
                    header[:] = (20, 20, 20)
                    
                    status_col = (0, 0, 255) if "AMB" in reason else (0, 255, 255)
                    cv2.putText(header, f"ADMIN MODE | Status: {reason}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_col, 2)
                    cv2.putText(header, "[S] Report | [Q] Exit", (w-300, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                    
                    final_screen = np.vstack((header, dashboard))
                    if w > 1300: final_screen = cv2.resize(final_screen, (1280, 720))

                    # SNAPSHOT
                    if any_ambulance_now and (time.time() - last_snapshot_time > 10):
                        ts = datetime.datetime.now().strftime("%H%M%S")
                        fn = f"evidence/AMB_{ts}.jpg"
                        cv2.imwrite(fn, final_screen)
                        print(f"📸 EVIDENCE SAVED: {fn}")
                        last_snapshot_time = time.time()

                    cv2.imshow("Traffic Admin Console", final_screen)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'): break
                    elif key == ord('s'):
                        msg = db.export_report()
                        messagebox.showinfo("Report", msg)

                for cap in caps.values(): cap.release()
                cv2.destroyAllWindows()
        else:
            print("❌ Login Failed or Cancelled.")

    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        messagebox.showerror("System Error", str(e))