import time

class TrafficManager:
    def __init__(self):
        # Config
        self.MIN_TIME = 5
        self.MAX_TIME = 60
        
        # Starvation Logic (Kaun kitni der se wait kar raha hai)
        # Format: {'Lane 1': last_green_time_timestamp}
        self.last_served = {
            'Lane 1': time.time(),
            'Lane 2': time.time(),
            'Lane 3': time.time(),
            'Lane 4': time.time()
        }
        
        # Agar koi 2 minute (120s) se khada hai, to use Priority do
        self.STARVATION_LIMIT = 120 

    def decide_signals(self, lane_data):
        """
        Advanced Logic to decide WHO goes next and for HOW LONG.
        Input lane_data structure:
        {
            'Lane 1': {'count': 10, 'load': 25, 'ambulance': False},
            ...
        }
        """
        current_time = time.time()
        
        # --- 1. EMERGENCY CHECK ---
        for lane, info in lane_data.items():
            if info['ambulance']:
                self.last_served[lane] = current_time # Update served time
                return {
                    'green_lane': lane,
                    'timer': 15, # Quick Pass
                    'reason': '🚑 AMBULANCE PRIORITY'
                }

        # --- 2. STARVATION CHECK (Fairness) ---
        # Kya koi lane bohot der se roti hui wait kar rahi hai?
        starved_lane = None
        max_wait = 0
        
        for lane, last_time in self.last_served.items():
            wait_time = current_time - last_time
            if wait_time > self.STARVATION_LIMIT and lane_data[lane]['count'] > 0:
                if wait_time > max_wait:
                    max_wait = wait_time
                    starved_lane = lane
        
        if starved_lane:
            self.last_served[starved_lane] = current_time
            return {
                'green_lane': starved_lane,
                'timer': 20, # Fixed time to clear backlog
                'reason': '⚠️ STARVATION RELEASE (Too much wait)'
            }

        # --- 3. DENSITY & LOAD LOGIC (Machine Learning Foundation) ---
        # Sort by LOAD (Not just count)
        # Example: Lane 1 has Load 50 (Trucks), Lane 2 has Load 20 (Cars) -> Lane 1 wins
        
        sorted_lanes = sorted(lane_data.items(), key=lambda x: x[1]['load'], reverse=True)
        
        winner_lane = sorted_lanes[0][0]
        winner_load = sorted_lanes[0][1]['load']
        
        # Timer Logic: 1 Load unit approx 0.8 seconds (Tunable)
        calc_time = winner_load * 0.8
        final_time = max(self.MIN_TIME, min(calc_time, self.MAX_TIME))
        
        # Agar bilkul traffic nahi hai
        if winner_load == 0:
             return {'green_lane': 'All Red', 'timer': 2, 'reason': 'No Traffic'}

        self.last_served[winner_lane] = current_time
        return {
            'green_lane': winner_lane,
            'timer': final_time,
            'reason': f'High Load ({winner_load})'
        }