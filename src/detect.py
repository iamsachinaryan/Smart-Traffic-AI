from ultralytics import YOLO
import cv2
import math
import cvzone
import numpy as np
import os
from collections import deque

class TrafficDetector:
    def __init__(self):
        print("🚀 Loading Triple-Engine Detection System...")
        
        # --- ENGINE 1: STANDARD YOLO ---
        self.model = YOLO("yolov8n.pt")
        
        # --- ENGINE 2: CUSTOM MODEL (Optional) ---
        self.custom_model = None
        self.custom_path = "models/custom_ambulance.pt"
        if os.path.exists(self.custom_path):
            print("✅ Custom Ambulance Model Loaded")
            self.custom_model = YOLO(self.custom_path)
        else:
            print("ℹ️ Using Hybrid Logic (No custom model found)")

        # --- ENGINE 3: HYBRID HEURISTICS CONFIG ---
        self.history = deque(maxlen=5) # Last 5 frames for temporal smoothing
        
        # Weights for score calculation
        self.WEIGHTS = {
            'color': 0.30,  # White body + Red stripes
            'shape': 0.20,  # Boxy aspect ratio
            'edge': 0.15,   # Vertical lines (van structure)
            'text': 0.20,   # Text-like patterns
            'light': 0.15   # Bright spots (Sirens)
        }

        self.classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                           "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                           "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                           "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                           "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                           "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                           "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                           "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                           "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                           "teddy bear", "hair drier", "toothbrush"]

    # --- 1. COLOR ANALYSIS (White Body + Red/Blue) ---
    def check_color(self, img_crop):
        if img_crop.size == 0: return 0
        hsv = cv2.cvtColor(img_crop, cv2.COLOR_BGR2HSV)
        total_pixels = img_crop.shape[0] * img_crop.shape[1]
        
        # White (Body)
        white_mask = cv2.inRange(hsv, np.array([0, 0, 168]), np.array([172, 111, 255]))
        white_ratio = cv2.countNonZero(white_mask) / total_pixels
        
        # Red (Stripes/Cross)
        red_mask1 = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255]))
        red_mask2 = cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255]))
        red_ratio = (cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)) / total_pixels
        
        score = 0
        if white_ratio > 0.3: score += 0.6
        if red_ratio > 0.05: score += 0.4
        return min(score, 1.0)

    # --- 2. SHAPE ANALYSIS (Aspect Ratio & Size) ---
    def check_shape(self, w, h):
        ratio = w / h
        # Ambulances are boxy vans (Ratio 1.3 to 2.8)
        if 1.3 < ratio < 2.8: return 1.0
        elif 1.0 < ratio < 3.5: return 0.5
        return 0

    # --- 3. EDGE PATTERN (Boxy vs Curved) ---
    def check_edges(self, img_crop):
        gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        # Count vertical lines (Ambulances have many vertical edges unlike cars)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
        detected = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        edge_density = cv2.countNonZero(detected) / (img_crop.shape[0] * img_crop.shape[1])
        return 1.0 if edge_density > 0.05 else 0.3

    # --- 4. TEXT REGION DETECTION (Contrast Blocks) ---
    def check_text_regions(self, img_crop):
        gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
        # Adaptive threshold to find text-like high contrast areas
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        text_score = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Look for small rectangular blocks (letters)
            if 0.2 < w/h < 1.0 and 5 < h < 30:
                text_score += 1
        return min(text_score / 10, 1.0)

    # --- 5. FLASHING LIGHTS (Bright Spots) ---
    def check_lights(self, img_crop):
        gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
        # Find very bright spots (Siren lights)
        _, bright = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        bright_ratio = cv2.countNonZero(bright) / (img_crop.shape[0] * img_crop.shape[1])
        # Sirens are small bright spots (not whole image like sky)
        if 0.03 < bright_ratio < 0.15: return 1.0 
        return 0

    # --- WEATHER CHECK (Phase 8 Logic) ---
    def check_weather(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        contrast = np.std(gray)
        if avg_brightness < 60: return "🌙 NIGHT / LOW LIGHT", True
        elif contrast < 35: return "🌫️ FOG / SMOG ALERT", True
        return "☀️ CLEAR WEATHER", False

    # === MAIN ANALYSIS FUNCTION ===
    def analyze_frame(self, frame):
        results = self.model(frame, stream=True, verbose=False)
        breakdown = {'car': 0, 'bike': 0, 'heavy': 0, 'rickshaw': 0}
        total_load = 0
        is_ambulance = False
        ambulance_confidence = 0
        
        weather_status, bad_weather = self.check_weather(frame)
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                currentClass = self.classNames[cls]

                if conf > 0.4:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w, h = x2 - x1, y2 - y1
                    
                    # Skip tiny objects
                    if w < 50 or h < 50: continue

                    # Basic Counting
                    if currentClass == "car":
                        breakdown['car'] += 1; total_load += 1
                        self.draw_box(frame, box, "Car", (255, 0, 255))
                    elif currentClass in ["motorbike", "bicycle"]:
                        breakdown['bike'] += 1; total_load += 1
                        self.draw_box(frame, box, "Bike", (0, 255, 255))
                    
                    # --- AMBULANCE DETECTION LOGIC ---
                    # Check ANY large vehicle (Bus, Truck, Car)
                    if currentClass in ["bus", "truck", "car"]:
                        
                        # Crop image for analysis
                        crop = frame[max(0,y1):min(y2,frame.shape[0]), max(0,x1):min(x2,frame.shape[1])]
                        
                        # Calculate Method Scores
                        s_color = self.check_color(crop)
                        s_shape = self.check_shape(w, h)
                        s_edge = self.check_edges(crop)
                        s_text = self.check_text_regions(crop)
                        s_light = self.check_lights(crop)
                        
                        # Weighted Sum
                        final_score = (s_color * self.WEIGHTS['color'] +
                                       s_shape * self.WEIGHTS['shape'] +
                                       s_edge * self.WEIGHTS['edge'] +
                                       s_text * self.WEIGHTS['text'] +
                                       s_light * self.WEIGHTS['light'])
                        
                        # HYBRID DECISION THRESHOLD (> 0.55 means likely Ambulance)
                        if final_score > 0.55:
                            is_ambulance = True
                            ambulance_confidence = final_score
                            
                            # Special RED Drawing for Ambulance
                            self.draw_ambulance_box(frame, x1, y1, x2, y2, final_score)
                            
                            # Don't double count as heavy/car if it's ambulance
                            continue 
                        
                        # If not ambulance but heavy
                        if currentClass in ["bus", "truck"]:
                            breakdown['heavy'] += 1; total_load += 2
                            self.draw_box(frame, box, "Heavy", (0, 165, 255))

        # --- CUSTOM MODEL OVERRIDE (If Available) ---
        if self.custom_model:
            c_results = self.custom_model(frame, stream=True, verbose=False)
            for r in c_results:
                for box in r.boxes:
                    if box.conf[0] > 0.6:
                        is_ambulance = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        self.draw_ambulance_box(frame, x1, y1, x2, y2, float(box.conf[0]))

        # Temporal Smoothing (Reduce flickering)
        self.history.append(is_ambulance)
        # Only confirm if detected in 3 out of last 5 frames
        confirmed_ambulance = sum(self.history) >= 3

        load_score = min(total_load * 4, 100) 
        return frame, breakdown, load_score, confirmed_ambulance, weather_status, bad_weather

    # Standard Box
    def draw_box(self, img, box, label, color):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cvzone.cornerRect(img, (x1, y1, x2-x1, y2-y1), l=9, rt=2, colorR=color)
        cvzone.putTextRect(img, f'{label}', (max(0, x1), max(35, y1)), scale=1, thickness=1, offset=3, colorR=color)

    # Special Ambulance Box
    def draw_ambulance_box(self, img, x1, y1, x2, y2, score):
        w, h = x2 - x1, y2 - y1
        # Flashing Red Border
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
        # Add "Priority" Label
        label = f"AMBULANCE {int(score*100)}%"
        cv2.rectangle(img, (x1, y1-30), (x1+200, y1), (0, 0, 255), -1)
        cv2.putText(img, label, (x1+5, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)