import sqlite3
import numpy as np

class Predictor:
    def __init__(self, db_manager):
        self.db = db_manager

    # Humne parameter ka naam 'current_hour' rakh diya hai taaki error na aaye
    def predict_load(self, day_of_week, current_hour):
        """
        Calculates the average traffic load for a specific day and hour
        based on historical data stored in the database.
        """
        try:
            # Connect directly to DB for read operation
            conn = sqlite3.connect("data/traffic_logs.db")
            cursor = conn.cursor()
            
            # Query: Average load for this specific Day & Hour
            cursor.execute("""
                SELECT AVG(load_score) 
                FROM signal_logs 
                WHERE day_of_week = ? AND hour = ?
            """, (day_of_week, current_hour))
            
            result = cursor.fetchone()
            conn.close()
            
            # Agar data hai to return karo, nahi to 0
            if result and result[0] is not None:
                return int(result[0])
            else:
                return 0
                
        except Exception as e:
            print(f"Prediction Error: {e}")
            return 0