# 🚦 Smart Traffic Management System (AI-Powered)

> **“Making Roads Smarter, Safer, and Faster”**

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![AI](https://img.shields.io/badge/AI-YOLOv8-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Prototype_Ready-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-Copyrighted-red?style=for-the-badge)

---

## 🌟 About the Project

The **Smart Traffic Management System** is an AI-powered intelligent traffic control solution designed to reduce traffic congestion, improve road safety, and provide instant priority to emergency vehicles.

Unlike traditional fixed-timer traffic signals, this system uses **Computer Vision** and **Artificial Intelligence** to analyze real-time traffic conditions through cameras and dynamically control traffic lights based on vehicle density.

**This project is not just an academic submission — it is a Smart City–ready prototype capable of transforming urban traffic infrastructure.** 🏙️

---

## 👨‍💻 Development Team

| Role | Name | Contribution |
| :--- | :--- | :--- |
| **Lead Developer** | **Sachin Aryan** | AI Logic, Backend, System Architecture |
| **Developer** | **Abhay Raj** | Data Collection, Testing, Hardware Integration |
| **UI & Design** | **Saloni Kumari** | Dashboard Layout, Graphics (B.Com, Shankar College) |

---

## 🚀 Key Features

### 🧠 1. Dual-Engine AI System
The system utilizes the **YOLOv8 Deep Learning Model** combined with custom traffic logic to detect vehicles with **95% accuracy**.
* ✔ Detects Cars, Bikes, Buses, Trucks, and Heavy Vehicles.
* ✔ Real-time processing with ultra-low latency.

### 🚑 2. Green Corridor (Ambulance Priority)
**Saving lives is our highest priority.**
* 🚨 If an ambulance is detected, the traffic signal automatically turns **GREEN**.
* ⏱ Normal signal timers are overridden immediately.
* 🚑 The ambulance passes without stopping (Zero Waiting Time).

### 🚫 3. Smart Stop-Line System
* The virtual **STOP LINE** appears only when the signal is **RED**.
* It disappears automatically when the signal turns **GREEN**.
* This reduces visual clutter and ensures accurate violation detection.

### 👮 4. Automatic E-Challan System
* **Violation Detection:** If a vehicle crosses the stop line during a RED signal, the system triggers an alert.
* 📸 **Evidence Capture:** An image of the vehicle is captured instantly.
* 💾 **Database Logging:** The violation is stored securely for E-Challan generation.
* 🔊 **Audio Alert:** A warning sound is played.

### 📊 5. Advanced Analytics Dashboard
The Admin Dashboard provides real-time traffic insights using professional visualization tools:
* 📈 **Bar Charts:** Peak traffic hour analysis.
* 🥧 **Pie Charts:** Vehicle type distribution.
* 📉 **Line Graphs:** Traffic density trends over time.

### ⚙️ 6. Admin Control Room
A secure control panel for administrators:
* 🔐 **Secure Login:** Username & Password authentication.
* ⚙️ **Settings Panel:** Adjust Green signal timers, switch themes (Dark/Light Mode).
* 🛑 **Manual Override:** Force GREEN signal for any lane during emergencies.

---

## 🛠️ Technology Stack

This project is built entirely using **Python** and advanced AI libraries:

| Component | Technology Used |
| :--- | :--- |
| **Language** | Python 3.x 🐍 |
| **Computer Vision** | OpenCV & CvZone 👁️ |
| **AI Model** | Ultralytics YOLOv8 🤖 |
| **GUI/Dashboard** | Tkinter & Pillow 🖼️ |
| **Data Visualization** | Matplotlib 📊 |
| **Database** | SQLite 🗄️ |

---
---

## 📥 Installation & Setup

Follow these steps to run the project locally on your machine:

**1️⃣ Clone the Repository**
```bash
git clone [https://github.com/iamsachinaryan/Smart-Traffic-AI](https://github.com/iamsachinaryan/Smart-Traffic-AI)

2️⃣ Navigate to Project Directory

Bash

cd Smart-Traffic-AI
3️⃣ Install Required Libraries

Bash

pip install -r requirements.txt
4️⃣ Run the Application

Bash

python dashboard.py
📁 Project Structure
Bash

Smart-Traffic-AI/
│
├── dashboard.py        # Main Application Entry Point
├── requirements.txt    # List of Dependencies
├── config.json         # System Configuration (Timers, Admin Info)
├── weights/            # YOLOv8 Trained Model Files
├── evidence/           # Auto-saved Traffic Violation Images
├── assets/             # UI Icons, Logos & Graph Images
└── README.md           # Project Documentation
🎯 Why This Project Matters
✅ Reduces Traffic Congestion: Smart timer allocation based on density. ✅ Saves Lives: Instant Green Corridor for Ambulances. ✅ Improves Road Safety: strict enforcement of Red Light violations. ✅ Eco-Friendly: Reduces fuel wastage caused by idling at signals. ✅ Smart City Ready: Scalable architecture for real-world deployment.

📜 License & Copyright
© 2025 Sachin Aryan All Rights Reserved.

This project is developed for academic and educational purposes. Unauthorized commercial use, reproduction, or distribution of this code without explicit permission is strictly prohibited.
