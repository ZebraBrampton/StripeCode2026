import random

# The simulation tracks a 12-hour operational day from 10:00 AM (10) to 9:00 PM (21)
HOURS = list(range(10, 22))

# Matrix mapping how weather impact categories dynamically dictate the behavior of each ride
RIDE_LOGIC = {
    "Lazy River":        {"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "FULL", "Wind (High)": "SLOW", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"},
    "Nebula Spinner":    {"Rain (Mod)": "SLOW", "Rain (High)": "SLOW", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Pixel Arcade":      {"Rain (Mod)": "FULL", "Rain (High)": "FULL", "Wind (Mod)": "FULL", "Wind (High)": "FULL", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Rocket Slingshot":  {"Rain (Mod)": "STOP", "Rain (High)": "STOP", "Wind (Mod)": "STOP", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Splashing Mountain":{"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"},
    "Titan Coaster":     {"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"}
}

class PureWeatherEngine:
    def __init__(self):
        """Initializes weather baselines with a wide spread to ensure varied start conditions"""
        self.rain = random.randint(1, 5)    
        self.wind = random.randint(10, 35)  
        self.temp = random.randint(20, 30)  

    def evolve_weather(self, hour):
        """Generates realistic, gradual hourly weather changes based on the previous hour."""
        # 1. Temperature Trend: Rises during the morning/afternoon, drops later in evening
        if hour <= 15:
            temp_change = random.randint(-1, 4) 
        else:
            temp_change = random.randint(-4, 1) 
        self.temp = max(18, min(45, self.temp + temp_change))

        # 2. Dynamic Rainfall Shift
        self.rain = max(0, min(10, self.rain + random.randint(-3, 3)))

        # 3. Enhanced Wind and Rain Correlation
        if self.rain >= 7:    
            self.wind = max(35, min(60, self.wind + random.randint(5, 15)))
        elif self.rain >= 4:  
            self.wind = max(21, min(42, self.wind + random.randint(-5, 10)))
        else:                 
            self.wind = max(5, min(25, self.wind + random.randint(-8, 5)))

    def get_impacts(self):
        """Converts raw numerical input values into structured impact levels"""
        rain_imp = "Low" if self.rain <= 3 else "Moderate" if self.rain <= 6 else "High"
        wind_imp = "Low" if self.wind <= 20 else "Moderate" if self.wind <= 40 else "High"
        temp_imp = "Low" if self.temp <= 25 else "Moderate" if self.temp <= 32 else "High"
        return rain_imp, wind_imp, temp_imp


class CoreSimulation:
    def __init__(self):
        self.weather = PureWeatherEngine()
        self.simulation_results = {} 

    def calculate_ride_state(self, ride_name, rain_imp, wind_imp, temp_imp):
        """Decision Logic: Evaluates severe conditions to determine operational overrides."""
        statuses = []
        rules = RIDE_LOGIC[ride_name]

        if rain_imp == "Moderate" and "Rain (Mod)" in rules: statuses.append(rules["Rain (Mod)"])
        if rain_imp == "High" and "Rain (High)" in rules: statuses.append(rules["Rain (High)"])
        if wind_imp == "Moderate" and "Wind (Mod)" in rules: statuses.append(rules["Wind (Mod)"])
        if wind_imp == "High" and "Wind (High)" in rules: statuses.append(rules["Wind (High)"])
        if temp_imp == "Moderate" and "Temp (Mod)" in rules: statuses.append(rules["Temp (Mod)"])
        if temp_imp == "High" and "Temp (High)" in rules: statuses.append(rules["Temp (High)"])

        if "STOP" in statuses: return "STOP"
        if "SLOW" in statuses: return "SLOW"
        return "FULL"

    def run_full_day(self):
        """Executes a continuous loop processing code over the 12-hour simulation cycle"""
        for hour in HOURS:
            self.weather.evolve_weather(hour)
            rain_imp, wind_imp, temp_imp = self.weather.get_impacts()

            ride_states = {}
            for ride in RIDE_LOGIC.keys():
                ride_states[ride] = self.calculate_ride_state(ride, rain_imp, wind_imp, temp_imp)

            # Combined data packet saving both raw weather values and the ride states
            self.simulation_results[hour] = {
                "weather_values": {
                    "rain": self.rain,
                    "wind": self.wind,
                    "temp": self.temp
                },
                "rides": ride_states
            }
            
        return self.simulation_results


# --- TEST RUN EXECUTION ---
if __name__ == "__main__":
    sim = CoreSimulation()
    day_log = sim.run_full_day()
    
    import pprint
    pprint.pprint(day_log)