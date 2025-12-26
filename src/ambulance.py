class AmbulanceSystem:
    def __init__(self):
        self.emergency_mode = False
        self.alert_message = ""

    def check_for_ambulance(self, detected_classes):
        """
        Checks if any emergency vehicle is in the list of detected objects.
        Standard YOLO uses 'truck' or 'bus' which we can use as proxy for ambulance in demo.
        """
        # Demo Logic: Agar Truck detect hua to use Ambulance maano
        # Real Logic: Custom Model training hoti hai
        
        emergency_vehicles = ['truck', 'bus'] # Demo ke liye hum truck ko ambulance maan rahe hain
        
        found = False
        for vehicle in detected_classes:
            if vehicle in emergency_vehicles:
                found = True
                break
        
        if found:
            self.emergency_mode = True
            self.alert_message = "🚑 AMBULANCE DETECTED! CLEARING TRAFFIC..."
            return True, self.alert_message
        else:
            self.emergency_mode = False
            return False, "Normal Traffic"