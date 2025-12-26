import datetime

class TrafficManager:
    def __init__(self, predictor):
        self.predictor = predictor

    def decide_phase(self, data):
        """
        Decides which lane gets the Green Signal and for how long.
        Prioritizes Ambulances > High Density > Prediction.
        """
        
        # --- 1. EMERGENCY CHECK (Phase 3: Green Corridor) ---
        for lane, info in data.items():
            if info['ambulance']: 
                print(f"🚨 EMERGENCY: Ambulance detected in {lane}!")
                return {
                    'active_pair': 'NS' if lane in ['North', 'South'] else 'EW',
                    'time': 60, 
                    'reason': f"🚨 GREEN CORRIDOR: {lane} (AMBULANCE)"
                }

        # --- 2. DENSITY CALCULATION ---
        load_ns = data['North']['load'] + data['South']['load']
        load_ew = data['East']['load'] + data['West']['load']
        
        # Default timings
        calc_time = 30
        active = 'NS'
        reason = "Balanced Traffic"

        # Compare Loads
        if load_ns > load_ew:
            active = 'NS'
            calc_time = max(20, min(60, load_ns * 1.5)) # Dynamic Time
            reason = f"High Density: NS ({load_ns})"
        elif load_ew > load_ns:
            active = 'EW'
            calc_time = max(20, min(60, load_ew * 1.5))
            reason = f"High Density: EW ({load_ew})"

        # --- 3. PREDICTION BOOST (Phase 2) ---
        # Future prediction add karte hain
        try:
            now = datetime.datetime.now()
            
            # ✅ FIX: Ab hum 'day' aur 'hour' dono bhej rahe hain
            pred_load = self.predictor.predict_load(now.weekday(), now.hour)
            
            if pred_load > 40: 
                calc_time += 10
                reason += " + Pred. Boost"
        except Exception as e:
            print(f"Logic Warning: {e}")

        return {
            'active_pair': active,
            'time': int(calc_time),
            'reason': reason
        }