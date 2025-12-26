# --- SYSTEM CONFIGURATION ---

# 1. Detection Settings
MODEL_PATH = "models/yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.45  # 45% sure hone par hi maano

# 2. Vehicle Weights (Phase 1 - Feature 2)
# Density Calculation ke liye points system
VEHICLE_WEIGHTS = {
    'motorbike': 1,
    'bicycle': 1,
    'auto': 2,      # Auto rickshaw
    'car': 2,
    'bus': 3,       # Badi gaadi = Zyada points
    'truck': 3
}

# 3. Signal Timing Limits (Seconds)
MIN_GREEN_TIME = 5
MAX_GREEN_TIME = 90
DEFAULT_YELLOW_TIME = 3

# 4. Emergency Config (Phase 1 - Feature 3)
EMERGENCY_CLASSES = ['ambulance', 'fire_truck']
EMERGENCY_CLEARANCE_TIME = 20  # Ambulance ke liye kitna time dena hai

# 5. Anti-Starvation (Phase 1 - Feature 4)
MAX_WAIT_CYCLES = 3  # Agar koi lane 3 baar se red hai, to use priority do