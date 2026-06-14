import random

HOURS = list(range(10, 22))

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
        self.rain = random.randint(0, 3)
        self.wind = random.randint(5, 25)
        self.temp = random.randint(22, 28)

    def evolve_weather(self, hour):
        if hour <= 15:
            temp_change = random.randint(-1, 3)
        else:
            temp_change = random.randint(-3, 1)
        self.temp = max(18, min(45, self.temp + temp_change))

        self.rain = max(0, min(10, self.rain + random.randint(-2, 2)))

        if self.rain >= 7:
            self.wind = max(41, min(60, self.wind + random.randint(-5, 10)))
        elif self.rain >= 4:
            self.wind = max(21, min(40, self.wind + random.randint(-10, 10)))
        else:
            self.wind = max(0, min(25, self.wind + random.randint(-10, 5)))

    def get_impacts(self):
        rain_imp = "Low" if self.rain <= 3 else "Moderate" if self.rain <= 6 else "High"
        wind_imp = "Low" if self.wind <= 20 else "Moderate" if self.wind <= 40 else "High"
        temp_imp = "Low" if self.temp <= 25 else "Moderate" if self.temp <= 32 else "High"
        return rain_imp, wind_imp, temp_imp


class CoreSimulation:
    def __init__(self):
        self.weather = PureWeatherEngine()
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

            # Pure structured data delivery
            self.simulation_results[hour] = ride_states
            
        return self.simulation_results

# --- EXECUTION ---
if __name__ == "__main__":
    sim = CoreSimulation()
    day_log = sim.run_full_day()
    
    # Printing the raw generated dictionary layout directly
    for i in day_log:
        print(i)
        for j in day_log[i]:
            print("\t",day_log[i][j])