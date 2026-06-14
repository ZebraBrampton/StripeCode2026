import random
import csv
import pprint

HOURS = list(range(10, 22))

RIDE_LOGIC = {
    "Lazy River":        {"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "FULL", "Wind (High)": "SLOW", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"},
    "Nebula Spinner":    {"Rain (Mod)": "SLOW", "Rain (High)": "SLOW", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Pixel Arcade":      {"Rain (Mod)": "FULL", "Rain (High)": "FULL", "Wind (Mod)": "FULL", "Wind (High)": "FULL", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Rocket Slingshot":  {"Rain (Mod)": "STOP", "Rain (High)": "STOP", "Wind (Mod)": "STOP", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Splashing Mountain":{"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"},
    "Titan Coaster":     {"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"}
}

# Configuration variables that can be extracted or imported from an external config file
SIMULATION_MODE = "CSV"  # Options: "RANDOM" or "CSV"
CSV_FILE_PATH = "International/ride_rush_weather_data.csv"

class PureWeatherEngine:
    def __init__(self, mode="RANDOM", csv_path=None):
        """Initializes weather engine. Can use either random baseline or load a given dataset."""
        self.mode = mode
        self.csv_data = {}
        
        # Load given dataset if mode is CSV
        if self.mode == "CSV" and csv_path:
            try:
                with open(csv_path, mode='r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        h = int(row['Hour'])
                        self.csv_data[h] = {
                            "rain": int(row['Rainfall_Intensity']),
                            "wind": int(row['Wind_Speed']),
                            "temp": int(row['Temperature'])
                        }
            except Exception as e:
                print(f"Error loading CSV, falling back to RANDOM mode: {e}")
                self.mode = "RANDOM"
                
        # Starting values for RANDOM mode
        self.rain = random.randint(1, 5)    
        self.wind = random.randint(10, 35)  
        self.temp = random.randint(20, 30)  

    def evolve_weather(self, hour):
        """Updates weather conditions based on either the loaded dataset or random trends."""
        if self.mode == "CSV":
            if hour in self.csv_data:
                self.rain = self.csv_data[hour]["rain"]
                self.wind = self.csv_data[hour]["wind"]
                self.temp = self.csv_data[hour]["temp"]
            return
            
        # --- RANDOM TREND LOGIC ---
        if hour <= 15:
            temp_change = random.randint(-1, 4) 
        else:
            temp_change = random.randint(-4, 1) 
        self.temp = max(18, min(45, self.temp + temp_change))

        self.rain = max(0, min(10, self.rain + random.randint(-3, 3)))

        if self.rain >= 7:    
            self.wind = max(35, min(60, self.wind + random.randint(5, 15)))
        elif self.rain >= 4:  
            self.wind = max(21, min(42, self.wind + random.randint(-5, 10)))
        else:                 
            self.wind = max(5, min(25, self.wind + random.randint(-8, 5)))

    def get_impacts(self):
        """Translates exact metrics into simple categories for safety evaluations."""
        rain_imp = "Low" if self.rain <= 3 else "Moderate" if self.rain <= 6 else "High"   
        wind_imp = "Low" if self.wind <= 20 else "Moderate" if self.wind <= 40 else "High" 
        temp_imp = "Low" if self.temp <= 25 else "Moderate" if self.temp <= 32 else "High" 
        return rain_imp, wind_imp, temp_imp


class CoreSimulation:
    def __init__(self, mode="RANDOM", csv_path=None):
        self.weather = PureWeatherEngine(mode=mode, csv_path=csv_path)
        self.simulation_results = {}

    def calculate_ride_state(self, ride_name, rain_imp, wind_imp, temp_imp):
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
        for hour in HOURS:
            self.weather.evolve_weather(hour)
            rain_imp, wind_imp, temp_imp = self.weather.get_impacts()

            ride_states = {}
            for ride in RIDE_LOGIC.keys():
                ride_states[ride] = self.calculate_ride_state(ride, rain_imp, wind_imp, temp_imp)

            self.simulation_results[hour] = {
                "weather_values": {
                    "rain": self.weather.rain,
                    "wind": self.weather.wind,
                    "temp": self.weather.temp
                },
                "rides": ride_states
            }
            
        return self.simulation_results

sim = CoreSimulation(mode=SIMULATION_MODE, csv_path=CSV_FILE_PATH)
res = sim.run_full_day()

if __name__ == "__main__":
    pprint(res)