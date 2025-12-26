import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import traceback
import datetime
import sys

# --- PATH FIX ---
sys.path.append(os.getcwd())

# --- CUSTOM MODULES ---
from detect import TrafficDetector
from logic import TrafficManager
from database import TrafficDB
from prediction import Predictor
import config

# ==========================================
# 1. ADMIN LOGIN SYSTEM
# ==========================================
class AdminLogin:
    def __init__(self):
        self.is_logged_in = False
        self.root = tk.Tk()
        self.root.title("Secure Login - Traffic AI")
        self.root.geometry("400x480")
        self.root.configure(bg="#121212")
        self.root.resizable(False, False)

        tk.Label(self.root, text="🛡️", font=("Arial", 60), bg="#121212", fg="#00cec9").pack(pady=(40, 10))
        tk.Label(self.root, text="CONTROL ROOM", font=("Segoe UI", 16, "bold"), bg="#121212", fg="white").pack(pady=10)

        tk.Label(self.root, text="Admin ID", bg="#121212", fg="gray").pack(anchor="w", padx=50)
        self.user_entry = tk.Entry(self.root, font=("Arial", 12), bg="#2d3436", fg="white", bd=0)
        self.user_entry.pack(fill="x", padx=50, pady=5, ipady=5)
        self.user_entry.focus()

        tk.Label(self.root, text="Password", bg="#121212", fg="gray").pack(anchor="w", padx=50, pady=(15, 0))
        self.pass_entry = tk.Entry(self.root, font=("Arial", 12), bg="#2d3436", fg="white", bd=0, show="*")
        self.pass_entry.pack(fill="x", padx=50, pady=5, ipady=5)

        self.root.bind('<Return>', self.verify)
        tk.Button(self.root, text="ACCESS SYSTEM", command=self.verify, bg="#0984e3", fg="white", font=("Arial", 11, "bold"), width=20, height=2, bd=0).pack(pady=40)
        self.root.mainloop()

    def verify(self, event=None):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        if u == "admin" and p == "admin123":
            self.is_logged_in = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Wrong ID or Password!")

# ==========================================
# 2. SETUP LAUNCHER (Return Point)
# ==========================================
class VideoLauncher:
    def __init__(self):
        self.video_paths = {}
        self.root = tk.Tk()
        self.root.title("System Configuration")
        self.root.geometry("600x550")
        self.root.configure(bg="#1e1e1e")

        tk.Label(self.root, text="🚦 Feed Configuration", font=("Segoe UI", 20, "bold"), bg="#1e1e1e", fg="#00cec9").pack(pady=20)
        
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

        tk.Button(self.root, text="START AI ENGINE", command=self.start_sys, bg="#2ed573", fg="white", font=("Arial", 14, "bold"), width=25).pack(pady=40)
        self.ready = False
        self.root.mainloop()

    def select_file(self, direction):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
        if path:
            self.video_paths[direction] = path
            self.path_labels[direction].config(text=os.path.basename(path)[:20]+"...", fg="#2ed573")

    def start_sys(self):
        if not self.video_paths:
            messagebox.showerror("Wait!", "Select at least 1 video.")
            return
        self.ready = True
        self.root.destroy()

# ==========================================
# 3. UI DRAWER (Optimized)
# ==========================================
def draw_ui(video_frame, name, is_green, rem_time, load, amb, breakdown):
    h, w, _ = video_frame.shape
    sidebar_w = 120
    total_w = w + sidebar_w
    
    # Pre-allocate canvas (Faster)
    canvas = np.full((h, total_w, 3), (30, 30, 30), dtype=np.uint8)
    
    # --- LIGHTS ---
    cx = sidebar_w // 2
    c_off = (50, 50, 50)
    c_red = (0, 0, 255) if not is_green else c_off
    c_grn = (0, 255, 0) if is_green else c_off
    
    cv2.circle(canvas, (cx, 40), 18, c_red, -1)
    cv2.circle(canvas, (cx, 40), 18, (0,0,0), 2)
    cv2.circle(canvas, (cx, 85), 18, c_off, -1)
    cv2.circle(canvas, (cx, 85), 18, (0,0,0), 2)
    cv2.circle(canvas, (cx, 130), 18, c_grn, -1)
    cv2.circle(canvas, (cx, 130), 18, (0,0,0), 2)
    
    # --- STATS ---
    y = 180
    f = cv2.FONT_HERSHEY_SIMPLEX
    cv2.line(canvas, (10, 165), (sidebar_w-10, 165), (100,100,100), 1)
    
    cv2.putText(canvas, f"Car :{breakdown['car']}", (10, y), f, 0.45, (200,200,200), 1)
    cv2.putText(canvas, f"Bike:{breakdown['bike']}", (10, y+25), f, 0.45, (200,200,200), 1)
    cv2.putText(canvas, f"Hvy :{breakdown['heavy']}", (10, y+50), f, 0.45, (200,200,200), 1)
    
    cv2.putText(canvas, "DENSITY", (20, y+90), f, 0.5, (0,255,255), 1)
    
    if load > 50:
        cv2.putText(canvas, str(load), (25, y+125), f, 1.2, (0,0,255), 3)
    else:
        cv2.putText(canvas, str(load), (25, y+125), f, 1.2, (0,255,0), 2)

    # --- VIDEO ---
    canvas[:, sidebar_w:] = video_frame
    
    # --- BOTTOM BAR ---
    # Overlay method slightly optimized
    cv2.rectangle(canvas, (sidebar_w, h-35), (total_w, h), (20,20,20), -1)
    
    t_str = f"{rem_time}s" if rem_time > 0 else "--"
    amb_txt = "DETECTED!" if amb else "No"
    amb_col = (0,0,255) if amb else (150,150,150)
    
    cv2.putText(canvas, f"Time: {t_str}", (sidebar_w+20, h-10), f, 0.6, (255,255,255), 1)
    cv2.putText(canvas, f"Amb: {amb_txt}", (sidebar_w+160, h-10), f, 0.6, amb_col, 2)
    cv2.putText(canvas, name, (total_w-100, 25), f, 0.7, (255,255,255), 2)
    
    return canvas

# ==========================================
# 4. MAIN LOOP (LOOP BACK ARCHITECTURE)
# ==========================================
if __name__ == "__main__":
    try:
        # STEP 1: Login (Run Once)
        login = AdminLogin()
        
        if login.is_logged_in:
            if not os.path.exists("evidence"): os.makedirs("evidence")
            
            # --- MAIN APP LOOP (Keeps coming back here) ---
            while True:
                # STEP 2: Dashboard / Launcher
                launcher = VideoLauncher()
                
                # Agar user ne Dashboard close kar diya bina Start dabaye, to App band karo
                if not launcher.ready:
                    print("❌ App Closed by User.")
                    break
                
                print("🚀 Initializing High-Performance AI Core...")

                # Initialize AI Engine
                db = TrafficDB()
                pred = Predictor(db)
                brain = TrafficManager(pred)
                detector = TrafficDetector()
                
                caps = {d: cv2.VideoCapture(p) for d, p in launcher.video_paths.items()}
                
                # Configuration
                pair_ns = ['North', 'South']
                pair_ew = ['East', 'West']
                active_pair = 'NS'
                timer_end = time.time() + 5
                reason = "Start"
                
                frame_counter = 0
                SKIP_FRAMES = 2 # Optimized Speed
                W, H = 600, 360
                
                default_bk = {'car': 0, 'bike': 0, 'heavy': 0, 'rickshaw': 0}
                last_data = {d: {'load': 0, 'ambulance': False, 'breakdown': default_bk} for d in caps}
                last_visuals = {}
                last_snap = 0
                
                user_exit = False # Flag to check if 'Q' was pressed

                print("✅ System Live. Press 'Q' to return to Dashboard.")

                # --- AI PROCESSING LOOP ---
                while True:
                    frame_counter += 1
                    curr_data = {}
                    visuals_map = {}
                    any_amb = False

                    # 1. READ & PROCESS
                    for d, cap in caps.items():
                        ret, frame = cap.read()
                        if not ret:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            ret, frame = cap.read()
                            if not ret: frame = np.zeros((H, W, 3), dtype=np.uint8)
                        
                        frame = cv2.resize(frame, (W, H))
                        
                        if frame_counter % (SKIP_FRAMES + 1) == 0:
                            p_frame, bk, load, is_amb = detector.analyze_frame(frame)
                            last_data[d] = {'load': load, 'ambulance': is_amb, 'breakdown': bk}
                            last_visuals[d] = p_frame
                            if is_amb: any_amb = True
                        
                        curr_data[d] = last_data[d]
                        visuals_map[d] = last_visuals.get(d, frame).copy()

                    # 2. LOGIC
                    rem = int(timer_end - time.time())
                    if rem <= 0:
                        rem = 0
                        dec = brain.decide_phase(curr_data)
                        active_pair = dec['active_pair']
                        timer_end = time.time() + dec['time']
                        reason = dec['reason']
                        if active_pair != "ALL_RED":
                            db.log_signal(active_pair, 0, 0, dec['time'], False)
                        print(f"🔄 {active_pair} -> {reason}")

                    # 3. DISPLAY
                    panels = []
                    for d in ['North', 'South', 'East', 'West']:
                        if d in visuals_map:
                            src = visuals_map[d]
                            is_g = (active_pair=='NS' and d in pair_ns) or (active_pair=='EW' and d in pair_ew)
                            p = draw_ui(src, d, is_g, rem, last_data[d]['load'], last_data[d]['ambulance'], last_data[d]['breakdown'])
                        else:
                            empty = np.zeros((H, W, 3), dtype=np.uint8)
                            p = draw_ui(empty, d, False, 0, 0, False, default_bk)
                        panels.append(p)
                    
                    top = np.hstack((panels[0], panels[1]))
                    bot = np.hstack((panels[2], panels[3]))
                    grid = np.vstack((top, bot))
                    
                    # Header
                    dh, dw, _ = grid.shape
                    head = np.zeros((50, dw, 3), dtype=np.uint8)
                    head[:] = (20,20,20)
                    cv2.putText(head, f"STATUS: {reason}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
                    cv2.putText(head, "[S] Report   [Q] Return to Dashboard", (dw-350, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)
                    
                    final = np.vstack((head, grid))
                    if dw > 1300: final = cv2.resize(final, (1280, 720))
                    
                    # Snapshot
                    if any_amb and (time.time() - last_snap > 10):
                        ts = datetime.datetime.now().strftime("%H%M%S")
                        fn = f"evidence/AMB_{ts}.jpg"
                        cv2.imwrite(fn, final)
                        print(f"📸 SNAPSHOT: {fn}")
                        last_snap = time.time()

                    cv2.imshow("Traffic Control AI", final)
                    
                    k = cv2.waitKey(1) & 0xFF
                    if k == ord('q'): 
                        user_exit = True
                        break # Break Inner Loop
                    if k == ord('s'):
                        msg = db.export_report()
                        print(msg)

                # --- CLEANUP BEFORE RETURNING TO DASHBOARD ---
                print("🔄 Returning to Dashboard...")
                for cap in caps.values(): cap.release()
                cv2.destroyAllWindows()
                
                # Loop wapas start hoga -> Launcher khulega
        
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error", str(e))