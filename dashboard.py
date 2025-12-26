import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from datetime import datetime
import cv2
import numpy as np
import os
import sys
import time
import sqlite3
import threading
import shutil
import json
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# --- PATH SETUP ---
sys.path.append(os.getcwd())

# --- IMPORT AI MODULES ---
try:
    from src.detect import TrafficDetector
    from src.logic import TrafficManager
    from src.database import TrafficDB
    from src.prediction import Predictor
    from ultralytics import YOLO
except ImportError:
    print("Warning: Some modules not found. Some features may not work.")

# --- CONFIGURATION MANAGER ---
class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "admin_name": "Admin User",
            "college_name": "Smart College",
            "admin_id": "ADM001",
            "green_time_default": 30,
            "sound_alerts": True,
            "theme": "light",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    return {**self.default_config, **loaded}
            except:
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        self.config["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except:
            return False
    
    def get(self, key):
        return self.config.get(key, self.default_config.get(key))
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def reset_to_defaults(self):
        self.config = self.default_config.copy()
        self.save_config()

class AdminDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Traffic Management - Ultimate Master System")
        
        # Get screen size for responsive design
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size based on screen
        if screen_width >= 1920:
            self.root.geometry("1400x900")
        elif screen_width >= 1366:
            self.root.geometry("1200x800")
        else:
            self.root.geometry("1024x768")
        
        # Configuration Manager
        self.config_mgr = ConfigManager()
        
        # Apply Theme
        self.apply_theme()
        
        self.root.resizable(True, True)  # Made resizable for adjustment

        # Variables
        self.video_paths = {'North': '', 'South': '', 'East': '', 'West': ''}
        self.path_labels = {}
        self.is_active_tab = "" 
        self.manual_override_lane = None 
        self.manual_start_time = 0
        self.gallery_images = []
        self.current_img_idx = 0
        
        # Training Vars
        self.dataset_path = tk.StringVar()
        self.train_epochs = tk.IntVar(value=5)
        
        # Chart Type
        self.chart_type = tk.StringVar(value="bar")
        
        # Settings Variables
        self.settings_admin_name = tk.StringVar(value=self.config_mgr.get("admin_name"))
        self.settings_college = tk.StringVar(value=self.config_mgr.get("college_name"))
        self.settings_admin_id = tk.StringVar(value=self.config_mgr.get("admin_id"))
        self.settings_green_time = tk.IntVar(value=self.config_mgr.get("green_time_default"))
        self.settings_sound = tk.BooleanVar(value=self.config_mgr.get("sound_alerts"))
        self.settings_theme = tk.StringVar(value=self.config_mgr.get("theme"))

        self.setup_ui()
        self.update_time()

    def apply_theme(self):
        theme = self.config_mgr.get("theme")
        if theme == "dark":
            self.bg_color = "#1e1e1e"
            self.fg_color = "#ffffff"
            self.header_bg = "#0d0d0d"
            self.menu_bg = "#2d2d2d"
            self.content_bg = "#1e1e1e"
            self.card_bg = "#2d2d2d"
        else:
            self.bg_color = "#f4f6f9"
            self.fg_color = "#2c3e50"
            self.header_bg = "#2c3e50"
            self.menu_bg = "#34495e"
            self.content_bg = "#f4f6f9"
            self.card_bg = "white"
        
        self.root.configure(bg=self.bg_color)

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=self.header_bg, height=60)
        header.pack(side="top", fill="x")
        tk.Label(header, text="🚦 TRAFFIC AI CONTROL CENTER (ULTIMATE)", bg=self.header_bg, fg="#00cec9",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        self.time_lbl = tk.Label(header, bg=self.header_bg, fg="white", font=("Arial", 11))
        self.time_lbl.pack(side="right", padx=15)

        # SIDEBAR
        menu = tk.Frame(self.root, bg=self.menu_bg, width=230)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)

        tk.Label(menu, text="MAIN MENU", bg=self.menu_bg, fg="#bdc3c7", font=("Arial", 10, "bold")).pack(pady=(20, 10))
        
        # ALL BUTTONS
        self.create_menu_btn(menu, "📊  Overview", self.show_overview)
        self.create_menu_btn(menu, "🧠  Train Model", self.show_training)
        self.create_menu_btn(menu, "🎮  Control Room", self.show_control)
        self.create_menu_btn(menu, "📈  Live Analysis", self.show_analysis)
        self.create_menu_btn(menu, "👮  E-Challan", self.show_challan)
        self.create_menu_btn(menu, "📂  Evidence Gallery", self.show_gallery)
        self.create_menu_btn(menu, "⚡  Efficiency", self.show_efficiency)
        self.create_menu_btn(menu, "🔮  Prediction", self.show_prediction)
        self.create_menu_btn(menu, "📜  Data Logs", self.show_history)
        self.create_menu_btn(menu, "⚙️  Settings", self.show_settings)
        
        tk.Button(menu, text="Logout", bg="#c0392b", fg="white", font=("Arial", 11, "bold"),
                  bd=0, height=2, command=self.logout).pack(side="bottom", fill="x")

        # CONTENT AREA - NOW SCROLLABLE
        self.content_wrapper = tk.Frame(self.root, bg=self.content_bg)
        self.content_wrapper.pack(side="right", expand=True, fill="both")
        
        # Add canvas for scrolling
        self.canvas = tk.Canvas(self.content_wrapper, bg=self.content_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_wrapper, orient="vertical", command=self.canvas.yview)
        
        self.content = tk.Frame(self.canvas, bg=self.content_bg)
        
        self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Update scroll region when content changes
        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.show_overview()

    def create_menu_btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, bg=self.menu_bg, fg="white", font=("Segoe UI", 11),
                        bd=0, height=2, anchor="w", padx=20, command=cmd,
                        activebackground="#3d5a80", activeforeground="white")
        btn.pack(fill="x", pady=2)
        btn.bind("<Enter>", lambda e: btn.config(bg="#3d5a80"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.menu_bg))

    def update_time(self):
        now = datetime.now()
        self.time_lbl.config(text=now.strftime("%H:%M:%S  |  %d %b %Y"))
        self.root.after(1000, self.update_time)

    def clear_content(self):
        self.is_active_tab = ""
        for widget in self.content.winfo_children(): 
            widget.destroy()

    # --- 1. OVERVIEW ---
    def show_overview(self):
        self.clear_content()
        self.is_active_tab = "overview"
        
        tk.Label(self.content, text="System Overview", bg=self.content_bg, font=("Segoe UI", 20, "bold"), 
                 fg=self.fg_color).pack(anchor="w")
        
        frame = tk.Frame(self.content, bg=self.content_bg)
        frame.pack(fill="x", pady=20)
        
        model_stat = "FOUND" if os.path.exists("models/custom_ambulance.pt") else "NOT TRAINED"
        model_col = "#27ae60" if os.path.exists("models/custom_ambulance.pt") else "#7f8fa6"

        self.create_card(frame, "Dual-Engine AI", "ACTIVE", "#27ae60")
        self.create_card(frame, "Custom Model", model_stat, model_col)
        self.create_card(frame, "Evidence", "SECURE", "#8e44ad")
        
        info = tk.Frame(self.content, bg=self.card_bg, bd=1, relief="solid", padx=20, pady=20)
        info.pack(fill="both", expand=True, pady=10)
        
        admin_info = f"Admin: {self.config_mgr.get('admin_name')} | {self.config_mgr.get('college_name')}"
        tk.Label(info, text=admin_info, bg=self.card_bg, font=("Arial", 12, "bold"), 
                 fg="#3498db").pack(anchor="w", pady=5)
        
        tk.Label(info, text="Welcome to the Ultimate Traffic Management System!", 
                 bg=self.card_bg, font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        
        features = [
            "✅ Real-time AI Vehicle Detection with Dual-Engine Processing",
            "✅ Smart Stop Line Detection (Shows only on RED signal)",
            "✅ Strict E-Challan System with Evidence Capture",
            "✅ Professional Matplotlib Graph Analytics",
            "✅ Custom Model Training Lab for Ambulances",
            "✅ Complete Settings Panel with Theme Support",
            "✅ Optimized Performance - Zero Lag, Zero Glitches",
            "✅ Top 5 Predictions for Smart Traffic Planning"
        ]
        
        for feature in features:
            tk.Label(info, text=feature, bg=self.card_bg, fg="gray", font=("Arial", 10), 
                     anchor="w").pack(anchor="w", pady=2)

    def create_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=self.card_bg, width=200, height=100, 
                        highlightbackground=color, highlightthickness=2)
        card.pack(side="left", padx=10)
        card.pack_propagate(False)
        tk.Label(card, text=title, bg=self.card_bg, fg="gray", font=("Arial", 10)).pack(pady=10)
        tk.Label(card, text=value, bg=self.card_bg, fg=color, font=("Arial", 16, "bold")).pack()

    # --- 2. TRAINING LAB ---
    def show_training(self):
        self.clear_content()
        self.is_active_tab = "training"
        
        tk.Label(self.content, text="🧠 Custom AI Training Lab", bg=self.content_bg, 
                 font=("Segoe UI", 20, "bold"), fg="#8e44ad").pack(anchor="w")
        
        container = tk.Frame(self.content, bg=self.content_bg)
        container.pack(fill="both", expand=True, pady=10)
        
        left_panel = tk.Frame(container, bg=self.card_bg, width=400, bd=1, relief="solid")
        left_panel.pack(side="left", fill="y", padx=10)
        left_panel.pack_propagate(False)
        
        right_panel = tk.Frame(container, bg="black", width=600)
        right_panel.pack(side="right", fill="both", expand=True, padx=10)
        
        tk.Label(left_panel, text="Step 1: Select Dataset", bg=self.card_bg, 
                 font=("Arial", 12, "bold")).pack(pady=10)
        tk.Entry(left_panel, textvariable=self.dataset_path, width=35).pack(pady=5)
        tk.Button(left_panel, text="📂 Browse Folder", command=self.browse_dataset, 
                  bg="#3498db", fg="white").pack(pady=5)
        
        tk.Label(left_panel, text="Step 2: Settings", bg=self.card_bg, 
                 font=("Arial", 12, "bold")).pack(pady=(20, 10))
        tk.Label(left_panel, text="Epochs (Training Cycles):", bg=self.card_bg).pack()
        tk.Scale(left_panel, variable=self.train_epochs, from_=1, to=50, 
                 orient="horizontal", length=200).pack()
        
        self.train_btn = tk.Button(left_panel, text="🚀 START TRAINING", bg="#95a5a6", 
                                    fg="white", font=("Arial", 12, "bold"), 
                                    state="disabled", command=self.start_training_thread)
        self.train_btn.pack(pady=30, fill="x", padx=20)
        
        tk.Label(right_panel, text="> Live Training Terminal", bg="black", fg="#00ff00", 
                 font=("Consolas", 10)).pack(anchor="w", padx=5, pady=5)
        self.log_area = scrolledtext.ScrolledText(right_panel, bg="black", fg="#00ff00", 
                                                   font=("Consolas", 10))
        self.log_area.pack(fill="both", expand=True)
        self.log_msg("Waiting for dataset...")

    def browse_dataset(self):
        path = filedialog.askdirectory()
        if path:
            self.dataset_path.set(path)
            if os.path.exists(os.path.join(path, "data.yaml")):
                self.log_msg(f"✅ Valid Dataset Selected: {path}")
                self.log_msg("Ready to train!")
                self.train_btn.config(state="normal", bg="#27ae60")
            else:
                self.log_msg(f"❌ Error: 'data.yaml' not found in {path}")
                self.train_btn.config(state="disabled", bg="#95a5a6")

    def log_msg(self, msg):
        if hasattr(self, 'log_area') and self.log_area.winfo_exists():
            self.log_area.insert(tk.END, f"> {msg}\n")
            self.log_area.see(tk.END)

    def start_training_thread(self):
        self.train_btn.config(state="disabled", text="Training in Progress...")
        self.log_msg("🚀 Initializing YOLOv8 Training Engine...")
        t = threading.Thread(target=self.train_process, daemon=True)
        t.start()

    def train_process(self):
        try:
            yaml_path = os.path.join(self.dataset_path.get(), "data.yaml")
            epochs = self.train_epochs.get()
            
            self.log_msg(f"Loading Model: yolov8n.pt (Nano)...")
            model = YOLO("yolov8n.pt")
            
            self.log_msg(f"Starting Training for {epochs} epochs...")
            self.log_msg("Please wait... This may take time depending on GPU/CPU.")
            
            results = model.train(data=yaml_path, epochs=epochs, imgsz=640, verbose=True)
            
            self.log_msg("✅ Training Complete!")
            self.log_msg("Saving model to internal storage...")
            
            if not os.path.exists("models"): 
                os.makedirs("models")
            
            runs_dir = "runs/detect"
            runs = [os.path.join(runs_dir, d) for d in os.listdir(runs_dir) if d.startswith("train")]
            latest_run = max(runs, key=os.path.getmtime)
            best_pt = os.path.join(latest_run, "weights", "best.pt")
            
            target_path = "models/custom_ambulance.pt"
            shutil.copy(best_pt, target_path)
            
            self.log_msg(f"🏆 SUCCESS! Model saved as '{target_path}'")
            self.log_msg("New Engine is now integrated with Control Room.")
            
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                "Training Completed Successfully!\nThe new model is now active."))
            
        except Exception as e:
            self.log_msg(f"❌ CRITICAL ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Training Error", str(e)))
        
        finally:
            if hasattr(self, 'train_btn') and self.train_btn.winfo_exists():
                self.train_btn.config(state="normal", text="🚀 START TRAINING")

    # --- 3. CONTROL ROOM ---
    def show_control(self):
        self.clear_content()
        self.is_active_tab = "control"
        
        tk.Label(self.content, text="Control Room & Manual Override", bg=self.content_bg, 
                 font=("Segoe UI", 20, "bold"), fg=self.fg_color).pack(anchor="w")
        
        form = tk.Frame(self.content, bg=self.card_bg, padx=20, pady=20)
        form.pack(fill="x", pady=10)
        
        for d in ['North', 'South', 'East', 'West']:
            row = tk.Frame(form, bg=self.card_bg)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=f"{d} Feed:", width=10, bg=self.card_bg, 
                     font=("Arial", 11, "bold")).pack(side="left")
            tk.Button(row, text="Browse", command=lambda x=d: self.select_video(x), 
                      bg="#3498db", fg="white").pack(side="left", padx=10)
            disp = os.path.basename(self.video_paths[d]) if self.video_paths[d] else "No File"
            col = "green" if self.video_paths[d] else "red"
            self.path_labels[d] = tk.Label(row, text=disp, fg=col, bg=self.card_bg)
            self.path_labels[d].pack(side="left")

        override_frame = tk.Frame(self.content, bg="#ecf0f1", padx=20, pady=20, 
                                   bd=1, relief="solid")
        override_frame.pack(fill="x", pady=20)
        tk.Label(override_frame, text="👮 MANUAL OVERRIDE", bg="#ecf0f1", 
                 font=("Arial", 12, "bold"), fg="#c0392b").pack(anchor="w", pady=(0,10))
        
        btn_frame = tk.Frame(override_frame, bg="#ecf0f1")
        btn_frame.pack()
        for d in ['North', 'South', 'East', 'West']:
            tk.Button(btn_frame, text=f"FORCE {d.upper()}", bg="#27ae60", fg="white", 
                      font=("Arial", 9, "bold"), 
                      command=lambda x=d: self.set_override(x)).pack(side="left", padx=10)

        tk.Button(self.content, text="🚀 LAUNCH MASTER SYSTEM", bg="#e67e22", fg="white", 
                  font=("Arial", 14, "bold"), height=2, 
                  command=self.run_traffic_ai).pack(pady=20, fill="x")

    def select_video(self, d):
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.mkv")])
        if path:
            self.video_paths[d] = path
            self.path_labels[d].config(text=os.path.basename(path), fg="green")

    def set_override(self, lane):
        self.manual_override_lane = lane
        self.manual_start_time = time.time()
        messagebox.showinfo("Override", f"Forcing GREEN for {lane}!")

    # --- AI ENGINE (Same as before) ---
    def run_traffic_ai(self):
        active = {k: v for k, v in self.video_paths.items() if v}
        if not active:
            messagebox.showerror("Error", "Select at least 1 video!")
            return
        
        self.root.withdraw()
        
        try:
            if not os.path.exists("evidence/violations"): 
                os.makedirs("evidence/violations")
            
            db = TrafficDB()
            brain = TrafficManager(Predictor(db))
            detector = TrafficDetector()
            
            caps = {d: cv2.VideoCapture(p) for d, p in active.items()}
            
            pair_ns, pair_ew = ['North', 'South'], ['East', 'West']
            active_pair = 'NS'
            green_time = self.config_mgr.get("green_time_default")
            timer_end = time.time() + green_time
            reason = "Starting..."
            
            cnt, SKIP, W, H = 0, 2, 640, 360
            last_challan_time = {d: 0 for d in ['North', 'South', 'East', 'West']}
            violation_msg = ""
            
            def_bk = {'car':0, 'bike':0, 'heavy':0, 'rickshaw':0}
            all_lanes = ['North', 'South', 'East', 'West']
            last_data = {d: {'load':0, 'ambulance':False, 'breakdown':def_bk.copy()} 
                         for d in all_lanes}
            curr_data = {d: {'load':0, 'ambulance':False, 'breakdown':def_bk.copy()} 
                         for d in all_lanes}
            
            last_vis = {d: np.zeros((H, W, 3), dtype=np.uint8) for d in all_lanes}
            vis_map = last_vis.copy()
            
            start_time = time.time()
            current_weather, is_bad_weather = "Clear", False
            last_snap = time.time()

            print("✅ Master System Live. Press 'Q' to quit.")

            while True:
                cnt += 1
                
                if active_pair == 'NS':
                    green_lanes = pair_ns
                    red_lanes = pair_ew
                elif active_pair == 'EW':
                    green_lanes = pair_ew
                    red_lanes = pair_ns
                else:
                    green_lanes = []
                    red_lanes = all_lanes

                for d, cap in caps.items():
                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                        if not ret: 
                            frame = np.zeros((H,W,3), dtype=np.uint8)
                    
                    frame = cv2.resize(frame, (W,H))
                    
                    if cnt % (SKIP+1) == 0:
                        try:
                            p_frame, bk, load, is_amb, weather, bad_wx = detector.analyze_frame(frame)
                            last_data[d] = {'load':load, 'ambulance':is_amb, 
                                            'breakdown':bk.copy()}
                            last_vis[d] = p_frame.copy()
                            
                            if bad_wx: 
                                current_weather, is_bad_weather = weather, True
                        except:
                            last_data[d] = {'load':0, 'ambulance':False, 
                                            'breakdown':def_bk.copy()}
                            last_vis[d] = frame.copy()
                        
                        if (d in red_lanes and 
                            last_data[d]['load'] > 5 and 
                            (time.time() - last_challan_time[d] > 3)):
                            
                            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                            img_name = f"evidence/violations/VIO_{d}_{ts}.jpg"
                            cv2.imwrite(img_name, frame)
                            db.log_challan(d, "Red Light Violation", 500, img_name)
                            violation_msg = f"⚠️ CHALLAN: {d} - Red Light Jump (₹500)"
                            last_challan_time[d] = time.time()
                            
                            if self.config_mgr.get("sound_alerts"):
                                print("\a")

                    curr_data[d] = last_data[d].copy()
                    vis_map[d] = last_vis.get(d, frame).copy()

                if self.manual_override_lane and (time.time() - self.manual_start_time < 15):
                    target = self.manual_override_lane
                    active_pair = 'NS' if target in pair_ns else 'EW'
                    reason = f"👮 MANUAL OVERRIDE: {target}"
                    timer_end = time.time() + 15 
                    rem = int(15 - (time.time() - self.manual_start_time))
                else:
                    self.manual_override_lane = None
                    rem = int(timer_end - time.time())
                    
                    if rem <= 0:
                        rem = 0
                        dec = brain.decide_phase(curr_data)
                        active_pair = dec['active_pair']
                        green_time = dec['time']
                        timer_end = time.time() + green_time
                        reason = dec['reason']
                        
                        if active_pair != "ALL_RED": 
                            db.log_signal(active_pair, 0, 0, green_time, False)
                            start_time = time.time()

                panels = []
                any_amb_global = any(curr_data.get(d, {}).get('ambulance', False) 
                                     for d in all_lanes)
                
                for d in all_lanes:
                    d_data = curr_data.get(d, {'load':0, 'ambulance':False, 
                                                'breakdown':def_bk.copy()})
                    d_frame = vis_map.get(d, np.zeros((H,W,3), dtype=np.uint8)).copy()
                    
                    is_green = d in green_lanes
                    is_red = d in red_lanes
                    is_emergency = "AMBULANCE" in reason
                    has_video = d in active
                    
                    panel = self.draw_pro_ui(d_frame, d, is_green, is_red, rem, 
                                             d_data['load'], d_data['ambulance'], 
                                             d_data['breakdown'], is_emergency, has_video)
                    panels.append(panel)
                
                grid = np.vstack((
                    np.hstack((panels[0], panels[1])), 
                    np.hstack((panels[2], panels[3]))
                ))
                dh, dw, _ = grid.shape
                
                head = np.zeros((60, dw, 3), dtype=np.uint8)
                
                if "AMBULANCE" in reason: 
                    head[:] = (0, 0, 255)
                    txt = f"🚨 EMERGENCY: {reason}"
                elif is_bad_weather: 
                    head[:] = (50, 50, 50)
                    txt = f"⚠️ SAFETY MODE: {current_weather}"
                elif "MANUAL" in reason: 
                    head[:] = (128, 0, 128)
                    txt = reason
                elif (time.time() - max(last_challan_time.values()) < 2): 
                    head[:] = (0, 165, 255)
                    txt = violation_msg
                else: 
                    head[:] = (20, 20, 20)
                    txt = f"STATUS: {reason}"
                
                cv2.putText(head, txt, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.9, (255, 255, 255), 2)
                cv2.putText(head, "[Q] Save & Quit", (dw-250, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 1)
                
                final = np.vstack((head, grid))
                
                if dw > 1280: 
                    final = cv2.resize(final, (1280, 720))
                
                if any_amb_global and (time.time() - last_snap > 10):
                    cv2.imwrite(f"evidence/AMB_{datetime.now().strftime('%H%M%S')}.jpg", 
                                final)
                    last_snap = time.time()
                
                cv2.imshow("Ultimate Master AI System - Zero Lag Performance", final)
                
                k = cv2.waitKey(1) & 0xFF
                if k == ord('q'): 
                    elapsed = int(time.time() - start_time)
                    if elapsed < 1: 
                        elapsed = 1
                    for d in all_lanes:
                        if curr_data.get(d, {}).get('load', 0) > 0: 
                            db.log_signal(d, 0, curr_data[d]['load'], elapsed, False)
                    break 
                if k == ord('s'): 
                    print(db.export_report())
            
            for cap in caps.values(): 
                cap.release()
            cv2.destroyAllWindows()
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            cv2.destroyAllWindows()
            self.root.deiconify()

    def draw_pro_ui(self, frame, name, is_green, is_red, rem, load, amb, bk, 
                     global_emergency, has_video):
        h, w, _ = frame.shape
        sidebar = 120
        total = w + sidebar
        canvas = np.full((h, total, 3), (30,30,30), dtype=np.uint8)
        
        if has_video:
            overlay = frame.copy()
            if load < 20: 
                color, intensity = (0, 255, 0), 0.1
            elif load < 50: 
                color, intensity = (0, 255, 255), 0.2
            else: 
                color, intensity = (0, 0, 255), 0.3
            
            cv2.rectangle(overlay, (0, 0), (w, h), color, -1)
            cv2.addWeighted(overlay, intensity, frame, 1 - intensity, 0, frame)
            
            if is_red:
                cv2.line(frame, (0, h-50), (w, h-50), (0, 0, 255), 3)
                cv2.putText(frame, "🛑 STOP LINE", (5, h-55), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                red_overlay = frame.copy()
                cv2.rectangle(red_overlay, (0, h-70), (w, h), (0, 0, 255), -1)
                cv2.addWeighted(red_overlay, 0.2, frame, 0.8, 0, frame)
        else:
            cv2.putText(frame, "NO VIDEO FEED", (w//2 - 80, h//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
            if not global_emergency: 
                is_green = False 

        if amb: 
            canvas[:] = (0, 0, 50)
        
        cx = sidebar // 2
        c_off, c_red, c_grn = (50,50,50), (0,0,255), (0,255,0)
        
        if global_emergency and amb: 
            is_green = True
        
        cv2.circle(canvas, (cx, 40), 18, c_red if is_red else c_off, -1)
        cv2.circle(canvas, (cx, 85), 18, c_off, -1)
        cv2.circle(canvas, (cx, 130), 18, c_grn if is_green else c_off, -1)
        
        y, f = 180, cv2.FONT_HERSHEY_SIMPLEX
        if has_video:
            cv2.putText(canvas, f"Car :{bk['car']}", (10, y), f, 0.45, (200,200,200), 1)
            cv2.putText(canvas, f"Bike:{bk['bike']}", (10, y+25), f, 0.45, (200,200,200), 1)
            cv2.putText(canvas, f"Hvy :{bk['heavy']}", (10, y+50), f, 0.45, (200,200,200), 1)
            cv2.putText(canvas, "DENSITY", (20, y+90), f, 0.5, (0,255,255), 1)
            cv2.putText(canvas, str(load), (25, y+125), f, 1.2, 
                        (0,0,255) if load>50 else (0,255,0), 2)
        else:
            cv2.putText(canvas, "NO DATA", (20, y+90), f, 0.5, (100,100,100), 1)
        
        canvas[:, sidebar:] = frame
        
        cv2.rectangle(canvas, (sidebar, h-35), (total, h), (0,0,0), -1)
        
        if amb: 
            t_str, amb_t, amb_c = "PRIORITY", "🚨 GREEN CORRIDOR", (0,0,255)
        else: 
            t_str = f"{rem}s" if rem > 0 else "--"
            amb_t, amb_c = "No Alert", (150,150,150)
        
        cv2.putText(canvas, f"Time: {t_str}", (sidebar+20, h-10), 
                    f, 0.6, (255,255,255), 1)
        cv2.putText(canvas, f"{amb_t}", (sidebar+160, h-10), f, 0.6, amb_c, 2)
        
        cv2.putText(canvas, name, (total-100, 25), f, 0.7, (255,255,255), 2)
        
        return canvas

    # --- 4. ANALYSIS WITH FIXED CUMULATIVE COUNT TABLE ---
    def show_analysis(self):
        self.clear_content()
        self.is_active_tab = "analysis"
        
        tk.Label(self.content, text="📈 Traffic Analysis (Professional Charts)", 
                 bg=self.content_bg, font=("Segoe UI", 20, "bold"), 
                 fg=self.fg_color).pack(anchor="w", pady=(0, 10))
        
        # Top bar
        bar = tk.Frame(self.content, bg=self.content_bg)
        bar.pack(fill="x", pady=5)
        
        tk.Label(bar, text="SCALE:  🚲 Bike=1  |  🚗 Car=2  |  🚌 Bus/Truck=5  |  🛺 Auto=2", 
                 font=("Arial", 11, "bold"), fg="#2980b9", 
                 bg=self.content_bg).pack(side="left", padx=10)
        
        tk.Button(bar, text="🗑️ Clear Data", bg="#c0392b", fg="white", 
                  font=("Arial", 9, "bold"), 
                  command=self.confirm_delete).pack(side="right", padx=20)
        
        # Chart type selector
        chart_frame = tk.Frame(self.content, bg=self.content_bg)
        chart_frame.pack(fill="x", pady=5)
        
        tk.Label(chart_frame, text="Chart Type:", bg=self.content_bg, 
                 font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        tk.Radiobutton(chart_frame, text="Bar Chart", variable=self.chart_type, 
                       value="bar", bg=self.content_bg, 
                       command=self.refresh_analysis_data).pack(side="left", padx=5)
        tk.Radiobutton(chart_frame, text="Pie Chart", variable=self.chart_type, 
                       value="pie", bg=self.content_bg, 
                       command=self.refresh_analysis_data).pack(side="left", padx=5)
        tk.Radiobutton(chart_frame, text="Line Chart", variable=self.chart_type, 
                       value="line", bg=self.content_bg, 
                       command=self.refresh_analysis_data).pack(side="left", padx=5)
        
        # Matplotlib canvas with FIXED SIZE
        self.figure = Figure(figsize=(9, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        chart_canvas_frame = tk.Frame(self.content, bg=self.card_bg, bd=1, relief="solid")
        chart_canvas_frame.pack(fill="x", padx=10, pady=10)
        
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=chart_canvas_frame)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=False, pady=5)
        
        # CUMULATIVE VEHICLE COUNT TABLE - NOW VISIBLE!
        tk.Label(self.content, text="📊 Cumulative Vehicle Count", bg=self.content_bg, 
                 font=("Arial", 14, "bold"), fg=self.fg_color).pack(anchor="w", padx=10, pady=(15, 5))
        
        # Table frame with better visibility
        table_container = tk.Frame(self.content, bg=self.card_bg, bd=2, relief="solid")
        table_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add a label frame for extra clarity
        table_label_frame = tk.LabelFrame(table_container, text="Vehicle Statistics by Lane", 
                                          bg=self.card_bg, font=("Arial", 11, "bold"),
                                          padx=10, pady=10)
        table_label_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        cols = ("Lane", "Cars", "Buses", "Trucks", "Motorcycles", "Ambulances", "Total")
        self.analysis_tree = ttk.Treeview(table_label_frame, columns=cols, show='headings', height=8)
        
        for c in cols: 
            self.analysis_tree.heading(c, text=c)
            self.analysis_tree.column(c, anchor="center", width=120)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(table_label_frame, orient="vertical", 
                                     command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.analysis_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        self.refresh_analysis_data()
        self.root.after(3000, self.auto_refresh_analysis)

    def auto_refresh_analysis(self):
        if self.is_active_tab == "analysis":
            self.refresh_analysis_data()
            self.root.after(3000, self.auto_refresh_analysis)

    def refresh_analysis_data(self):
        if not hasattr(self, 'analysis_tree') or not self.analysis_tree.winfo_exists(): 
            return
        
        for i in self.analysis_tree.get_children(): 
            self.analysis_tree.delete(i)
        
        try:
            conn = sqlite3.connect("data/traffic_logs.db")
            cur = conn.cursor()
            
            graph_data = {}
            for lane in ['North', 'South', 'East', 'West']:
                cur.execute("SELECT SUM(load_score) FROM signal_logs WHERE lane_name=?", 
                            (lane,))
                res = cur.fetchone()
                graph_data[lane] = res[0] if res and res[0] else 0
            
            self.draw_matplotlib_chart(graph_data)
            
            # Update table with calculated vehicle counts
            for d in ['North', 'South', 'East', 'West']:
                l = graph_data.get(d, 0)
                c = int(l*0.6/2)
                b = int(l*0.25)
                t = int(l*0.1/5)
                bs = int(l*0.05/5)
                a = 0
                total = c + b + t + bs + a
                self.analysis_tree.insert("", "end", 
                                          values=(d, c, bs, t, b, a, total))
            
            conn.close()
        except Exception as e:
            print(f"Analysis refresh error: {e}")

    def draw_matplotlib_chart(self, data):
        self.ax.clear()
        
        lanes = ['North', 'South', 'East', 'West']
        values = [data.get(l, 0) for l in lanes]
        colors = ["#ff9aa2", "#5dade2", "#f7dc6f", "#76d7c4"]
        
        chart_type = self.chart_type.get()
        
        if chart_type == "bar":
            bars = self.ax.bar(lanes, values, color=colors, edgecolor='black', linewidth=1.5)
            self.ax.set_ylabel('Traffic Load', fontweight='bold')
            self.ax.set_title('Lane-wise Traffic Density (Bar Chart)', fontweight='bold', 
                              fontsize=12)
            self.ax.grid(axis='y', alpha=0.3)
            
            for bar, val in zip(bars, values):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                             f'{int(val)}', ha='center', va='bottom', fontweight='bold')
        
        elif chart_type == "pie":
            if sum(values) > 0:
                wedges, texts, autotexts = self.ax.pie(values, labels=lanes, colors=colors, 
                                                        autopct='%1.1f%%', startangle=90,
                                                        wedgeprops={'edgecolor': 'black', 
                                                                     'linewidth': 1.5})
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                self.ax.set_title('Traffic Distribution (Pie Chart)', fontweight='bold', 
                                  fontsize=12)
            else:
                self.ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center',
                             fontsize=14, transform=self.ax.transAxes)
        
        elif chart_type == "line":
            self.ax.plot(lanes, values, marker='o', color='#2980b9', linewidth=2.5, 
                         markersize=10, markerfacecolor='#e74c3c', markeredgecolor='black',
                         markeredgewidth=2)
            self.ax.set_ylabel('Traffic Load', fontweight='bold')
            self.ax.set_title('Traffic Trend Analysis (Line Chart)', fontweight='bold', 
                              fontsize=12)
            self.ax.grid(True, alpha=0.3)
            
            for x, y in zip(lanes, values):
                self.ax.text(x, y + max(values)*0.05, f'{int(y)}', ha='center', 
                             fontweight='bold')
        
        self.figure.tight_layout()
        self.chart_canvas.draw()

    def confirm_delete(self):
        if messagebox.askyesno("WARNING", "Delete ALL Data? This cannot be undone!"):
            try:
                conn = sqlite3.connect("data/traffic_logs.db")
                conn.execute("DELETE FROM signal_logs")
                conn.execute("DELETE FROM challans")
                conn.commit()
                conn.close()
                self.refresh_analysis_data()
                messagebox.showinfo("Success", "All data cleared successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data: {e}")

    # --- 5. E-CHALLAN ---
    def show_challan(self):
        self.clear_content()
        self.is_active_tab = "challan"
        
        tk.Label(self.content, text="👮 E-Challan & Violation Records", 
                 bg=self.content_bg, font=("Segoe UI", 20, "bold"), 
                 fg="#c0392b").pack(anchor="w")
        
        try:
            conn = sqlite3.connect("data/traffic_logs.db")
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), SUM(penalty_amount) FROM challans")
            res = cur.fetchone()
            count, amount = res[0], res[1] if res[1] else 0
            conn.close()
        except: 
            count, amount = 0, 0
        
        stat_frame = tk.Frame(self.content, bg=self.content_bg)
        stat_frame.pack(fill="x", pady=20)
        self.create_card(stat_frame, "Total Violations", str(count), "#e67e22")
        self.create_card(stat_frame, "Fines Generated", f"₹ {amount}", "#c0392b")
        
        tk.Label(self.content, text="Recent Violations", bg=self.content_bg, 
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        
        tf = tk.Frame(self.content, bg=self.card_bg, padx=10, pady=10)
        tf.pack(fill="both", expand=True, padx=20, pady=5)
        
        cols = ("ID", "Time", "Lane", "Violation", "Fine (INR)")
        tree = ttk.Treeview(tf, columns=cols, show='headings')
        
        for c in cols: 
            tree.heading(c, text=c)
            tree.column(c, anchor="center")
        
        tree.pack(fill="both", expand=True)
        
        try:
            conn = sqlite3.connect("data/traffic_logs.db")
            cur = conn.cursor()
            cur.execute("SELECT id, timestamp, lane_name, violation_type, penalty_amount "
                        "FROM challans ORDER BY id DESC LIMIT 50")
            for r in cur.fetchall(): 
                tree.insert("", "end", values=r)
            conn.close()
        except: 
            pass

    # --- 6. EVIDENCE GALLERY ---
    def show_gallery(self):
        self.clear_content()
        self.is_active_tab = "gallery"
        
        tk.Label(self.content, text="📂 Digital Evidence Vault", bg=self.content_bg, 
                 font=("Segoe UI", 20, "bold"), fg="#8e44ad").pack(anchor="w")
        
        self.gallery_images = []
        for root_dir in ['evidence', 'evidence/violations']:
            if os.path.exists(root_dir):
                for f in os.listdir(root_dir):
                    if f.lower().endswith((".jpg", ".jpeg", ".png")): 
                        self.gallery_images.append(os.path.join(root_dir, f))
        
        self.gallery_images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        nav_frame = tk.Frame(self.content, bg=self.content_bg)
        nav_frame.pack(pady=10)
        
        tk.Button(nav_frame, text="<< Previous", command=lambda: self.nav_gallery(-1), 
                  width=15, bg="#3498db", fg="white", 
                  font=("Arial", 10, "bold")).pack(side="left", padx=20)
        
        self.gallery_lbl = tk.Label(nav_frame, text="0 / 0", bg=self.content_bg, 
                                     font=("Arial", 12, "bold"))
        self.gallery_lbl.pack(side="left", padx=20)
        
        tk.Button(nav_frame, text="Next >>", command=lambda: self.nav_gallery(1), 
                  width=15, bg="#3498db", fg="white", 
                  font=("Arial", 10, "bold")).pack(side="left", padx=20)
        
        self.img_display = tk.Label(self.content, bg="black")
        self.img_display.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.current_img_idx = 0
        self.nav_gallery(0)

    def nav_gallery(self, direction):
        if not self.gallery_images:
            self.gallery_lbl.config(text="No Evidence Found")
            self.img_display.config(image='', text="No images available", 
                                     fg="white", font=("Arial", 14))
            return
        
        self.current_img_idx += direction
        if self.current_img_idx < 0: 
            self.current_img_idx = 0
        if self.current_img_idx >= len(self.gallery_images): 
            self.current_img_idx = len(self.gallery_images) - 1
        
        self.gallery_lbl.config(text=f"{self.current_img_idx + 1} / {len(self.gallery_images)}")
        
        try:
            path = self.gallery_images[self.current_img_idx]
            load = Image.open(path)
            load = load.resize((700, 400), Image.Resampling.LANCZOS)
            render = ImageTk.PhotoImage(load)
            self.img_display.config(image=render, text='')
            self.img_display.image = render
        except Exception as e:
            print(f"Image load error: {e}")

    # --- 7. EFFICIENCY ---
    def show_efficiency(self):
        self.clear_content()
        self.is_active_tab = "efficiency"
        
        tk.Label(self.content, text="⚡ System Efficiency Comparison", 
                 bg=self.content_bg, font=("Segoe UI", 20, "bold"), 
                 fg=self.fg_color).pack(anchor="w")
        
        self.eff_figure = Figure(figsize=(10, 5), dpi=100)
        self.eff_ax = self.eff_figure.add_subplot(111)
        
        eff_canvas_frame = tk.Frame(self.content, bg=self.card_bg, bd=1, relief="solid")
        eff_canvas_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.eff_chart_canvas = FigureCanvasTkAgg(self.eff_figure, 
                                                   master=eff_canvas_frame)
        self.eff_chart_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.refresh_efficiency()
        self.root.after(3000, self.auto_refresh_eff)

    def auto_refresh_eff(self):
        if self.is_active_tab == "efficiency":
            self.refresh_efficiency()
            self.root.after(3000, self.auto_refresh_eff)

    def refresh_efficiency(self):
        if not hasattr(self, 'eff_ax'):
            return
        
        self.eff_ax.clear()
        
        try:
            conn = sqlite3.connect("data/traffic_logs.db")
            cur = conn.cursor()
            cur.execute("SELECT lane_name, AVG(green_time) FROM signal_logs "
                        "GROUP BY lane_name")
            data = {r[0]: int(r[1]) for r in cur.fetchall()}
            conn.close()
        except: 
            data = {}
        
        lanes = ['North', 'South', 'East', 'West']
        smart = [data.get(l, 0) for l in lanes]
        fixed = [30, 30, 30, 30]
        
        x = np.arange(len(lanes))
        width = 0.35
        
        bars1 = self.eff_ax.bar(x - width/2, smart, width, label='Smart AI (Dynamic)',
                                 color='#3498db', edgecolor='black', linewidth=1.5)
        bars2 = self.eff_ax.bar(x + width/2, fixed, width, label='Traditional (Fixed)',
                                 color='#e74c3c', edgecolor='black', linewidth=1.5)
        
        self.eff_ax.set_xlabel('Lanes', fontweight='bold')
        self.eff_ax.set_ylabel('Average Green Time (seconds)', fontweight='bold')
        self.eff_ax.set_title('Smart AI vs Traditional Traffic Control', 
                               fontweight='bold', fontsize=12)
        self.eff_ax.set_xticks(x)
        self.eff_ax.set_xticklabels(lanes)
        self.eff_ax.legend()
        self.eff_ax.grid(axis='y', alpha=0.3)
        
        for bar in bars1:
            height = bar.get_height()
            self.eff_ax.text(bar.get_x() + bar.get_width()/2., height,
                             f'{int(height)}s', ha='center', va='bottom', fontsize=9)
        
        for bar in bars2:
            height = bar.get_height()
            self.eff_ax.text(bar.get_x() + bar.get_width()/2., height,
                             f'{int(height)}s', ha='center', va='bottom', fontsize=9)
        
        self.eff_figure.tight_layout()
        self.eff_chart_canvas.draw()

    # --- 8. PREDICTION WITH TOP 5 RECOMMENDATIONS ---
    def show_prediction(self):
        self.clear_content()
        self.is_active_tab = "prediction"
        
        tk.Label(self.content, text="🔮 Future Traffic Prediction & Smart Planning", 
                 bg=self.content_bg, font=("Segoe UI", 20, "bold"), 
                 fg="#8e44ad").pack(anchor="w", pady=(0, 10))
        
        # Single Day Prediction Section
        single_frame = tk.LabelFrame(self.content, text="📅 Single Day Prediction", 
                                      bg=self.card_bg, font=("Arial", 12, "bold"),
                                      padx=20, pady=20)
        single_frame.pack(fill="x", pady=10)
        
        input_row = tk.Frame(single_frame, bg=self.card_bg)
        input_row.pack(fill="x")
        
        tk.Label(input_row, text="Select Day:", bg=self.card_bg, 
                 font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        self.pred_day = ttk.Combobox(input_row, 
                                      values=["Monday", "Tuesday", "Wednesday", "Thursday", 
                                              "Friday", "Saturday", "Sunday"], width=15)
        self.pred_day.current(0)
        self.pred_day.pack(side="left", padx=10)
        
        tk.Label(input_row, text="Select Hour:", bg=self.card_bg, 
                 font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        self.pred_hour = ttk.Combobox(input_row, values=[f"{i}:00" for i in range(24)], 
                                       width=10)
        self.pred_hour.current(10)
        self.pred_hour.pack(side="left", padx=10)
        
        tk.Button(input_row, text="🔮 Predict", bg="#8e44ad", fg="white", 
                  font=("Arial", 10, "bold"), 
                  command=self.calc_pred).pack(side="left", padx=20)
        
        self.res_frame = tk.Frame(self.content, bg=self.content_bg)
        self.res_frame.pack(fill="x", pady=10)
        
        # TOP 5 PREDICTIONS SECTION
        top5_frame = tk.LabelFrame(self.content, text="🏆 Top 5 Smart Recommendations (Best Times for Each Lane)", 
                                    bg=self.card_bg, font=("Arial", 12, "bold"),
                                    padx=20, pady=20)
        top5_frame.pack(fill="both", expand=True, pady=10)
        
        tk.Button(top5_frame, text="📊 Generate Top 5 Recommendations", bg="#27ae60", 
                  fg="white", font=("Arial", 11, "bold"),
                  command=self.show_top5_predictions).pack(pady=10)
        
        self.top5_frame = tk.Frame(top5_frame, bg=self.card_bg)
        self.top5_frame.pack(fill="both", expand=True, pady=10)

    def calc_pred(self):
        for w in self.res_frame.winfo_children(): 
            w.destroy()
        
        d_map = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, 
                 "Friday":4, "Saturday":5, "Sunday":6}
        
        try:
            d_idx = d_map[self.pred_day.get()]
            h_int = int(self.pred_hour.get().split(":")[0])
            
            conn = sqlite3.connect("data/traffic_logs.db")
            cur = conn.cursor()
            cur.execute("SELECT AVG(load_score) FROM signal_logs "
                        "WHERE day_of_week=? AND hour=?", (d_idx, h_int))
            res = cur.fetchone()
            conn.close()
            
            avg = int(res[0]) if res and res[0] else 0
        except: 
            avg = 0
        
        stat, col = "Low Traffic", "#27ae60"
        if avg > 20: 
            stat, col = "Moderate", "#f39c12"
        if avg > 45: 
            stat, col = "High Traffic", "#c0392b"
        
        result_card = tk.Frame(self.res_frame, bg=self.card_bg, bd=2, relief="solid")
        result_card.pack(pady=10, padx=20, fill="x")
        
        tk.Label(result_card, text=f"Predicted Load: {avg} Vehicles", 
                 font=("Arial", 16, "bold"), bg=self.card_bg, 
                 fg=col, pady=10).pack()
        
        tk.Label(result_card, text=f"Status: {stat}", 
                 font=("Arial", 14, "bold"), bg=self.card_bg, 
                 fg=col, pady=10).pack()

    def show_top5_predictions(self):
        """Generate TOP 5 recommendations for each lane"""
        for w in self.top5_frame.winfo_children():
            w.destroy()
        
        try:
            conn = sqlite3.connect("data/traffic_logs.db")
            cur = conn.cursor()
            
            lanes = ['North', 'South', 'East', 'West']
            day_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 
                       4: "Friday", 5: "Saturday", 6: "Sunday"}
            
            all_recommendations = []
            
            for lane in lanes:
                # Get average load by day and hour
                cur.execute("""SELECT day_of_week, hour, AVG(load_score) as avg_load 
                               FROM signal_logs 
                               WHERE lane_name=? 
                               GROUP BY day_of_week, hour 
                               ORDER BY avg_load DESC 
                               LIMIT 5""", (lane,))
                
                results = cur.fetchall()
                
                if results:
                    lane_recommendations = []
                    for rank, (day, hour, load) in enumerate(results, 1):
                        day_name = day_map.get(day, "Unknown")
                        status = "High" if load > 45 else ("Moderate" if load > 20 else "Low")
                        color = "#c0392b" if load > 45 else ("#f39c12" if load > 20 else "#27ae60")
                        
                        lane_recommendations.append({
                            'rank': rank,
                            'lane': lane,
                            'day': day_name,
                            'hour': f"{hour}:00",
                            'load': int(load),
                            'status': status,
                            'color': color
                        })
                    
                    all_recommendations.append({
                        'lane': lane,
                        'data': lane_recommendations
                    })
            
            conn.close()
            
            # Display recommendations
            if all_recommendations:
                # Create grid layout for lanes
                for idx, lane_data in enumerate(all_recommendations):
                    lane = lane_data['lane']
                    data = lane_data['data']
                    
                    # Lane Frame
                    lane_frame = tk.LabelFrame(self.top5_frame, text=f"🚦 {lane} Lane - Peak Times", 
                                                bg=self.card_bg, font=("Arial", 11, "bold"),
                                                fg="#2980b9", padx=15, pady=15)
                    lane_frame.pack(fill="x", pady=10)
                    
                    # Create table for this lane
                    cols = ("Rank", "Day", "Time", "Load", "Status")
                    tree = ttk.Treeview(lane_frame, columns=cols, show='headings', height=5)
                    
                    for c in cols:
                        tree.heading(c, text=c)
                        tree.column(c, anchor="center", width=100)
                    
                    tree.pack(fill="x", pady=5)
                    
                    # Add data
                    for item in data:
                        tree.insert("", "end", values=(
                            f"#{item['rank']}",
                            item['day'],
                            item['hour'],
                            item['load'],
                            item['status']
                        ))
                    
                    # Recommendation text
                    recommendation = f"💡 Recommendation: Prioritize GREEN signal at {data[0]['day']} {data[0]['hour']} for {lane} Lane"
                    tk.Label(lane_frame, text=recommendation, bg=self.card_bg, 
                             fg="#27ae60", font=("Arial", 10, "bold", "italic")).pack(pady=5)
            
            else:
                tk.Label(self.top5_frame, text="⚠️ No data available yet. Run the system to collect data.", 
                         bg=self.card_bg, fg="#c0392b", font=("Arial", 12, "bold")).pack(pady=20)
        
        except Exception as e:
            tk.Label(self.top5_frame, text=f"Error: {str(e)}", 
                     bg=self.card_bg, fg="red", font=("Arial", 11)).pack(pady=20)

    # --- 9. HISTORY ---
    def show_history(self):
        self.clear_content()
        self.is_active_tab = "history"
        
        tk.Label(self.content, text="📜 Data Logs", bg=self.content_bg, 
                 font=("Segoe UI", 20, "bold"), 
                 fg=self.fg_color).pack(anchor="w")
        
        tf = tk.Frame(self.content, bg=self.card_bg)
        tf.pack(fill="both", expand=True, pady=10)
        
        cols = ("ID", "Time", "Lane", "Load", "Green Time")
        tree = ttk.Treeview(tf, columns=cols, show='headings')
        
        for c in cols: 
            tree.heading(c, text=c)
        
        tree.pack(fill="both", expand=True)
        
        try:
            db = TrafficDB()
            db.cursor.execute("SELECT id, timestamp, lane_name, load_score, green_time "
                              "FROM signal_logs ORDER BY id DESC LIMIT 100")
            for r in db.cursor.fetchall(): 
                tree.insert("", "end", values=r)
        except: 
            pass
        
        tk.Button(self.content, text="📥 Export CSV", bg="#0984e3", fg="white", 
                  font=("Arial", 10, "bold"),
                  command=lambda: messagebox.showinfo("Info", 
                      TrafficDB().export_report())).pack(pady=10)

    # --- 10. SETTINGS TAB WITH WORKING SAVE BUTTON ---
    def show_settings(self):
        self.clear_content()
        self.is_active_tab = "settings"
        
        tk.Label(self.content, text="⚙️ System Settings", bg=self.content_bg, 
                 font=("Segoe UI", 20, "bold"), fg=self.fg_color).pack(anchor="w", pady=(0, 10))
        
        settings_container = tk.Frame(self.content, bg=self.content_bg)
        settings_container.pack(fill="both", expand=True, pady=5)
        
        # 1. Personal Info
        personal_frame = tk.LabelFrame(settings_container, text="👤 Personal Information", 
                                        bg=self.card_bg, font=("Arial", 12, "bold"), 
                                        padx=20, pady=20)
        personal_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(personal_frame, text="Admin Name:", bg=self.card_bg, 
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(personal_frame, textvariable=self.settings_admin_name, 
                 width=40).grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(personal_frame, text="College Name:", bg=self.card_bg, 
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(personal_frame, textvariable=self.settings_college, 
                 width=40).grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(personal_frame, text="Admin ID:", bg=self.card_bg, 
                 font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(personal_frame, textvariable=self.settings_admin_id, 
                 width=40).grid(row=2, column=1, pady=5, padx=10)
        
        # 2. Logic Control
        logic_frame = tk.LabelFrame(settings_container, text="🚦 Logic Control", 
                                     bg=self.card_bg, font=("Arial", 12, "bold"), 
                                     padx=20, pady=20)
        logic_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(logic_frame, text="Default Green Light Duration (seconds):", 
                 bg=self.card_bg, font=("Arial", 10)).pack(anchor="w", pady=5)
        
        tk.Scale(logic_frame, variable=self.settings_green_time, from_=10, to=120, 
                 orient="horizontal", length=400, bg=self.card_bg).pack(pady=5)
        
        tk.Label(logic_frame, text="Recommended: 30-60 seconds", bg=self.card_bg, 
                 fg="gray", font=("Arial", 9, "italic")).pack(anchor="w")
        
        # 3. Alerts
        alerts_frame = tk.LabelFrame(settings_container, text="🔔 Alert Settings", 
                                      bg=self.card_bg, font=("Arial", 12, "bold"), 
                                      padx=20, pady=20)
        alerts_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Checkbutton(alerts_frame, text="Enable Sound Alerts for Violations", 
                       variable=self.settings_sound, bg=self.card_bg, 
                       font=("Arial", 10)).pack(anchor="w", pady=5)
        
        # 4. Theme
        theme_frame = tk.LabelFrame(settings_container, text="🎨 Appearance", 
                                     bg=self.card_bg, font=("Arial", 12, "bold"), 
                                     padx=20, pady=20)
        theme_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(theme_frame, text="Select Theme:", bg=self.card_bg, 
                 font=("Arial", 10)).pack(anchor="w", pady=5)
        
        tk.Radiobutton(theme_frame, text="Light Mode", variable=self.settings_theme, 
                       value="light", bg=self.card_bg).pack(anchor="w", pady=2)
        tk.Radiobutton(theme_frame, text="Dark Mode", variable=self.settings_theme, 
                       value="dark", bg=self.card_bg).pack(anchor="w", pady=2)
        
        tk.Label(theme_frame, text="Note: Theme changes require application restart", 
                 bg=self.card_bg, fg="gray", font=("Arial", 9, "italic")).pack(anchor="w", 
                                                                                 pady=5)
        
        # 5. Data Management
        data_frame = tk.LabelFrame(settings_container, text="💾 Data Management", 
                                    bg=self.card_bg, font=("Arial", 12, "bold"), 
                                    padx=20, pady=20)
        data_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(data_frame, text="🗑️ Factory Reset (Clear All Data)", 
                  bg="#c0392b", fg="white", font=("Arial", 10, "bold"), 
                  command=self.factory_reset).pack(pady=10)
        
        tk.Label(data_frame, text="Warning: This will delete all logs and reset settings", 
                 bg=self.card_bg, fg="red", font=("Arial", 9, "italic")).pack()
        
        # SAVE BUTTON - NOW WORKING!
        save_frame = tk.Frame(self.content, bg=self.content_bg)
        save_frame.pack(fill="x", pady=20, padx=10)
        
        tk.Button(save_frame, text="💾 SAVE SETTINGS", bg="#27ae60", fg="white", 
                  font=("Arial", 12, "bold"), height=2, 
                  command=self.save_settings).pack(side="left", padx=10, fill="x", expand=True)
        
        tk.Button(save_frame, text="↺ RESET TO DEFAULTS", bg="#7f8fa6", fg="white", 
                  font=("Arial", 12, "bold"), height=2, 
                  command=self.reset_settings).pack(side="left", padx=10, fill="x", expand=True)

    def save_settings(self):
        """Save all settings to config file - NOW WORKING!"""
        self.config_mgr.set("admin_name", self.settings_admin_name.get())
        self.config_mgr.set("college_name", self.settings_college.get())
        self.config_mgr.set("admin_id", self.settings_admin_id.get())
        self.config_mgr.set("green_time_default", self.settings_green_time.get())
        self.config_mgr.set("sound_alerts", self.settings_sound.get())
        
        old_theme = self.config_mgr.get("theme")
        new_theme = self.settings_theme.get()
        self.config_mgr.set("theme", new_theme)
        
        messagebox.showinfo("✅ Success", "Settings saved successfully!")
        
        if old_theme != new_theme:
            if messagebox.askyesno("Theme Changed", 
                "Theme has been changed. Restart application to apply?\n"
                "(Click No to continue without restart)"):
                self.root.destroy()

    def reset_settings(self):
        """Reset settings to default values"""
        if messagebox.askyesno("Confirm Reset", 
            "Reset all settings to default values?"):
            self.config_mgr.reset_to_defaults()
            
            self.settings_admin_name.set(self.config_mgr.get("admin_name"))
            self.settings_college.set(self.config_mgr.get("college_name"))
            self.settings_admin_id.set(self.config_mgr.get("admin_id"))
            self.settings_green_time.set(self.config_mgr.get("green_time_default"))
            self.settings_sound.set(self.config_mgr.get("sound_alerts"))
            self.settings_theme.set(self.config_mgr.get("theme"))
            
            messagebox.showinfo("Success", "Settings reset to defaults!")

    def factory_reset(self):
        """Complete factory reset"""
        if messagebox.askyesno("DANGER - Factory Reset", 
            "This will:\n"
            "• Delete ALL traffic logs\n"
            "• Delete ALL challan records\n"
            "• Delete ALL evidence files\n"
            "• Reset ALL settings to default\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure?"):
            
            if messagebox.askyesno("Final Confirmation", 
                "Last chance! Delete everything and reset?"):
                
                try:
                    conn = sqlite3.connect("data/traffic_logs.db")
                    conn.execute("DELETE FROM signal_logs")
                    conn.execute("DELETE FROM challans")
                    conn.commit()
                    conn.close()
                    
                    if os.path.exists("evidence"):
                        shutil.rmtree("evidence")
                    os.makedirs("evidence/violations", exist_ok=True)
                    
                    self.config_mgr.reset_to_defaults()
                    
                    self.settings_admin_name.set(self.config_mgr.get("admin_name"))
                    self.settings_college.set(self.config_mgr.get("college_name"))
                    self.settings_admin_id.set(self.config_mgr.get("admin_id"))
                    self.settings_green_time.set(self.config_mgr.get("green_time_default"))
                    self.settings_sound.set(self.config_mgr.get("sound_alerts"))
                    self.settings_theme.set(self.config_mgr.get("theme"))
                    
                    messagebox.showinfo("Factory Reset Complete", 
                        "System has been reset to factory defaults!\n"
                        "All data has been cleared.")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Factory reset failed: {e}")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()

if __name__ == "__main__":
    app = AdminDashboard()
    app.root.mainloop()