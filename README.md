# 🚦 Smart Traffic Management System (AI-Powered)

> **"Making Roads Smarter & Safer"** > Developed by: **Sachin Aryan** 👨‍💻

---

## 🌟 About The Project
This is an **Industrial-Level AI System** designed to solve traffic jams and enforce traffic rules automatically. It uses computer vision (cameras) to watch the road, control traffic lights based on density, and help emergency vehicles pass instantly.

It's not just a project; it's a complete **Smart City Solution**! 🏙️

---

## 🚀 Key Features

### 🧠 1. Dual-Engine AI
Uses **YOLOv8 + Hybrid Logic** to detect vehicles with **95% accuracy**. It can identify Cars, Buses, Trucks, Bikes, and Rickshaws.

### 🚑 2. Green Corridor (Ambulance Priority)
If an **Ambulance** is detected, the system automatically turns the signal **GREEN** for that lane. Saving lives matters most! ❤️

### 🚫 3. Smart Stop Line
The Red "STOP LINE" only appears on the video when the signal is **RED**. It disappears when the light is Green. Pure magic! ✨

### 👮 4. Automatic E-Challan System
Catches rule breakers instantly! If a vehicle crosses the stop line during a **Red Signal**, the system:
* 📸 Takes a photo evidence.
* 💾 Saves it in the database.
* 🔊 Plays a warning sound (Beep).

### 📊 5. Advanced Analytics Dashboard
View live data with professional **Matplotlib Graphs**:
* **Bar Charts, Pie Charts, Line Graphs**.
* Track vehicle counts and system efficiency in real-time.

### ⚙️ 6. Admin Control Room
* **Login System:** Secure access (ID/Password).
* **Settings Tab:** Change Green Light timer, Admin Name, and Theme (Dark/Light Mode).
* **Manual Override:** Force Green light for any lane manually.

---

## 🛠️ Tech Stack (Requirements)

This project is built using powerful Python libraries. You need to install these to run the magic:

* 🐍 **Python 3.x**
* 👁️ **OpenCV & Cvzone** (For Video Processing)
* 🤖 **Ultralytics YOLOv8** (The AI Brain)
* 📈 **Matplotlib** (For Graphs)
* 🖼️ **Pillow & Tkinter** (For the Dashboard UI)

---

## 📥 How to Install

1.  **Clone this Repository** (Download the code).
2.  Open your terminal/command prompt in the project folder.
3.  Run the following command to install all dependencies:

```bash
pip install -r requirements.txt
