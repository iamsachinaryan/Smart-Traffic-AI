import sqlite3
import datetime
import os
import csv

class TrafficDB:
    def __init__(self, db_path="data/traffic_logs.db"):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Table 1: Traffic Logs
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                lane_name TEXT,
                load_score INTEGER,
                green_time INTEGER,
                hour INTEGER,
                day_of_week INTEGER
            )
        """)
        # Table 2: Violations (Challans) - PHASE 4
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS challans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                lane_name TEXT,
                violation_type TEXT,
                penalty_amount INTEGER,
                snapshot_path TEXT
            )
        """)
        self.conn.commit()

    def log_signal(self, lane, count, load, time_given, emergency):
        now = datetime.datetime.now()
        self.cursor.execute("""
            INSERT INTO signal_logs (timestamp, lane_name, load_score, green_time, hour, day_of_week)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (now, lane, load, time_given, now.hour, now.weekday()))
        self.conn.commit()

    # --- PHASE 4: LOG CHALLAN ---
    def log_challan(self, lane, v_type, amount, path):
        now = datetime.datetime.now()
        self.cursor.execute("""
            INSERT INTO challans (timestamp, lane_name, violation_type, penalty_amount, snapshot_path)
            VALUES (?, ?, ?, ?, ?)
        """, (now, lane, v_type, amount, path))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_total_challans(self):
        try:
            self.cursor.execute("SELECT COUNT(*), SUM(penalty_amount) FROM challans")
            return self.cursor.fetchone()
        except: return (0, 0)

    def export_report(self):
        filename = f"Traffic_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Traffic Data
                self.cursor.execute("SELECT * FROM signal_logs")
                writer.writerow(['--- TRAFFIC LOGS ---'])
                writer.writerow(['ID', 'Timestamp', 'Lane', 'Load', 'Green Time'])
                writer.writerows(self.cursor.fetchall())
                
                # Challan Data
                self.cursor.execute("SELECT * FROM challans")
                writer.writerow([])
                writer.writerow(['--- VIOLATION CHALLANS ---'])
                writer.writerow(['ID', 'Timestamp', 'Lane', 'Violation', 'Amount', 'Image'])
                writer.writerows(self.cursor.fetchall())
            
            return f"✅ Full Report Saved: {filename}"
        except Exception as e:
            return f"❌ Export Error: {e}"