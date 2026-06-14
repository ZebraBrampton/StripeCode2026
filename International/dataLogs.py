# =====================================================================
# CHUNK 1: SYSTEM SETUP & CONFIGURATION
# Imports tools, sets operational hours, and builds the ride rule matrix.
# =====================================================================
import random  # Imports random number generator tool.

HOURS = list(range(10, 22))  # Creates a list of hours from 10 to 21 (10 AM to 9 PM).

# Master safety dictionary mapping weather impact categories directly to ride states.
RIDE_LOGIC = {
    # If a condition isn't listed for a ride, it defaults to safe ("FULL").
    "Lazy River":        {"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "FULL", "Wind (High)": "SLOW", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"},
    "Nebula Spinner":    {"Rain (Mod)": "SLOW", "Rain (High)": "SLOW", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Pixel Arcade":      {"Rain (Mod)": "FULL", "Rain (High)": "FULL", "Wind (Mod)": "FULL", "Wind (High)": "FULL", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Rocket Slingshot":  {"Rain (Mod)": "STOP", "Rain (High)": "STOP", "Wind (Mod)": "STOP", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "FULL"},
    "Splashing Mountain":{"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"},
    "Titan Coaster":     {"Rain (Mod)": "SLOW", "Rain (High)": "STOP", "Wind (Mod)": "SLOW", "Wind (High)": "STOP", "Temp (Mod)": "FULL", "Temp (High)": "SLOW"}
}


# =====================================================================
# CHUNK 2: WEATHER GENERATION ENGINE
# Tracks raw values and applies environmental trends (like day/night temp shifts).
# =====================================================================
class PureWeatherEngine:
    def __init__(self):
        """Sets up the initial random weather baseline at park opening."""
        self.rain = random.randint(1, 5)    # Generates starting rain level between 1 and 5.
        self.wind = random.randint(10, 35)  # Generates starting wind speed between 10 and 35 km/h.
        self.temp = random.randint(20, 30)  # Generates starting temperature between 20°C and 30°C.

    def evolve_weather(self, hour):
        """Adjusts the variables hour-by-hour using sequential tracking rules."""
        # --- TEMPERATURE TREND LOGIC ---
        if hour <= 15:                          # Check if current time is 3:00 PM or earlier.
            temp_change = random.randint(-1, 4) # Forces temperature to trend warmer in afternoon.
        else:                                   # Triggered if current time is after 3:00 PM.
            temp_change = random.randint(-4, 1) # Forces temperature to trend cooler in evening.
        self.temp = max(18, min(45, self.temp + temp_change)) # Clamps temperature between 18°C and 45°C.

        # --- GRADUAL RAINFALL LOGIC ---
        self.rain = max(0, min(10, self.rain + random.randint(-3, 3))) # Shifts rain level by a max step of +/-3.

        # --- WIND AND RAIN CORRELATION LOGIC ---
        if self.rain >= 7:                      # Check if rain has escalated to a heavy storm.
            self.wind = max(35, min(60, self.wind + random.randint(5, 15)))  # Forces wind into high storm ranges.
        elif self.rain >= 4:                    # Check if rain is at a moderate shower level.
            self.wind = max(21, min(42, self.wind + random.randint(-5, 10))) # Keeps wind steady at medium speeds.
        else:                                   # Triggered if there is clear sky or light drizzle.
            self.wind = max(5, min(25, self.wind + random.randint(-8, 5)))   # Pulls wind speeds down smoothly.


# =====================================================================
# CHUNK 3: TRANSLATION LOGIC
# Converts raw numbers into structured categories (Low, Moderate, High).
# =====================================================================
    def get_impacts(self):
        """Translates exact metrics into simple categories for safety evaluations."""
        rain_imp = "Low" if self.rain <= 3 else "Moderate" if self.rain <= 6 else "High"   # Categorizes rain levels.
        wind_imp = "Low" if self.wind <= 20 else "Moderate" if self.wind <= 40 else "High" # Categorizes wind speeds.
        temp_imp = "Low" if self.temp <= 25 else "Moderate" if self.temp <= 32 else "High" # Categorizes temperature levels.
        return rain_imp, wind_imp, temp_imp  # Pushes all three descriptive categories back out.


# =====================================================================
# CHUNK 4: CORE PARK SIMULATOR & DECISION BRAIN
# Coordinates weather data, evaluates rules, and applies priority overrides.
# =====================================================================
class CoreSimulation:
    def __init__(self):
        """Initializes the manager engine instance."""
        self.weather = PureWeatherEngine()  # Connects the core weather system to the manager.
        self.simulation_results = {}        # Prepares a clean empty dictionary to store the entire day log.

    def calculate_ride_state(self, ride_name, rain_imp, wind_imp, temp_imp):
        """Compares current weather categories against a specific ride's rulebook."""
        statuses = []                       # Sets up a blank temporary list to hold triggered alerts.
        rules = RIDE_LOGIC[ride_name]       # Extracts the explicit rules dictionary for the specified ride.

        # --- RULE CHECKING PATTERN ---
        if rain_imp == "Moderate" and "Rain (Mod)" in rules: statuses.append(rules["Rain (Mod)"])     # Evaluates moderate rain.
        if rain_imp == "High" and "Rain (High)" in rules: statuses.append(rules["Rain (High)"])         # Evaluates severe rain.
        if wind_imp == "Moderate" and "Wind (Mod)" in rules: statuses.append(rules["Wind (Mod)"])     # Evaluates moderate wind.
        if wind_imp == "High" and "Wind (High)" in rules: statuses.append(rules["Wind (High)"])         # Evaluates severe wind.
        if temp_imp == "Moderate" and "Temp (Mod)" in rules: statuses.append(rules["Temp (Mod)"])     # Evaluates moderate temp.
        if temp_imp == "High" and "Temp (High)" in rules: statuses.append(rules["Temp (High)"])         # Evaluates severe temp.

        # --- SEVERITY PRIORITY OVERRIDES ---
        if "STOP" in statuses: return "STOP"  # If a danger condition exists, force immediate ride shutdown.
        if "SLOW" in statuses: return "SLOW"  # If a warning condition exists, slow operations down.
        return "FULL"                         # If no restrictions are present, run fully open.


# =====================================================================
# CHUNK 5: CONTINUOUS AUTOMATION LOOP
# Runs the 12-hour simulation cycle and structures the outputs.
# =====================================================================
    def run_full_day(self):
        """Automates the entire 12-hour operating loop from open to close."""
        for hour in HOURS:                     # Starts a loop running through hours 10 to 21 sequentially.
            self.weather.evolve_weather(hour)  # Updates weather data variables for the current hour step.
            rain_imp, wind_imp, temp_imp = self.weather.get_impacts() # Fetches the translated impact categories.

            ride_states = {}                   # Prepares a fresh dictionary to log statuses for this specific hour.
            for ride in RIDE_LOGIC.keys():     # Starts an inner loop spinning through each of the 6 main rides.
                # Runs decision engine rules and records the state for that specific ride.
                ride_states[ride] = self.calculate_ride_state(ride, rain_imp, wind_imp, temp_imp)

            # --- CONSOLIDATING MULTI-LEVEL DATA PACKET ---
            self.simulation_results[hour] = {  # Generates an entry under the current simulation hour key.
                "weather_values": {            # Opens a sub-dictionary dedicated to the physical metrics.
                    "rain": self.weather.rain, # Logs raw rainfall scale integer value.
                    "wind": self.weather.wind, # Logs raw wind velocity kilometer value.
                    "temp": self.weather.temp  # Logs raw temperature celsius value.
                },                             # Closes the numerical weather tracking block.
                "rides": ride_states           # Plugs the dictionary of ride statuses directly beside the weather stats.
            }                                  # Closes the complete data package for this hour.
            
        return self.simulation_results         # Outputs the complete 12-hour tracking dictionary once loop finishes.

sim = CoreSimulation()               # Spawns a new active simulation coordinator instance.
random_log = sim.run_full_day()         # Triggers the loop engine to simulate the entire operating day.

# =====================================================================
# CHUNK 6: IGNITION & TESTING INTERFACE
# The execution trigger used to run and verify the engine data format.
# =====================================================================
if __name__ == "__main__":               # Safety check ensuring file is run directly rather than imported.
    
    import pprint                        # Imports advanced terminal pretty-printer module layout.
    pprint.pprint(random_log)               # Prints out the raw dictionary directly to verify formatting is clean.