# Import all necessary libraries and modules
# Multiprocessing is used to create separate processes running simultaneously
from multiprocessing import Queue, Process

# Import the classes for the main window and second information window
from themeParkClass import ParkWindow
from rideClass import RideWindow

# Import the combinedDict that contains all data logs
from dataLogs import combinedDict

# Function to start the main window for theme park using theme_park process
def start_theme_park(caption, size, pos, queue_in, queue_out, images):
    park_window = ParkWindow(caption, size, pos, queue_in, queue_out, images)
    park_window.run()

# Function to start the second window for station information using ride_park process
def start_ride_window(caption, size, pos, queue_in, queue_out, logs):
    ride_window = RideWindow(caption, size, pos, queue_in, queue_out, logs)
    ride_window.run()

# Run program if this file is being run directly
if __name__ == "__main__":

    # Create a dictionary of all images
    images = {

        "Map" : ("Map", (0, 0), (0, 0, 0)),

        "Lazy River" : ("Lazy River", (454, 647), (159, 197, 232)),

        "Nebula Spinner" : ("Nebula Spinner", (459, 8), (249, 203, 156)),

        "Pixel Arcade" : ("Pixel Arcade", (25, 532), (0, 255, 255)),

        "Rocket Slingshot" : ("Rocket Slingshot", (189, 8), (255, 229, 153)),

        "Splashing Mountain" : ("Splashing Mountain", (478, 180), (147, 196, 125)),

        "Titan Coaster" : ("Titan Coaster", (17, 275), (139, 198, 252)),

        "Hydration Station" : ("Hydration Station", (450, 524), (164, 194, 244)),

        "Pixel Popcorn" : ("Pixel Popcorn", (253, 180), (230, 145, 56)),

        "Quantum Cafe" : ("Quantum Cafe", (176, 673), (142, 124, 195)),

        "The Sugar Shack" : ("The Sugar Shack", (244, 523), (233, 120, 93))

    }

    # Initialize the size and position args for the windows
    theme_park_size = (800, 900)
    station_size = (400, 900)
    
    theme_park_pos = (10 + 250, 25)
    station_pos = (820 + 250, 25)

    # Create IN/OUT queues for Theme Park
    main_to_park = Queue()
    park_to_main = Queue()

    # Create IN/OUT queues for Station
    main_to_station = Queue()
    station_to_main = Queue()

    # Create Main Window with communcation_queue
    theme_park = Process(
        target=start_theme_park, # Target function to start the main window for theme park
        args=("Theme Park", theme_park_size, theme_park_pos, main_to_park, park_to_main, images)
    )   # Parameters: (caption, size, pos, queue_in, queue_out, images)

    # Create Second Information Window with communcation_queue
    ride_park = Process(
        target=start_ride_window, # Target function to start the second window for station information
        args=("Station", station_size, station_pos, main_to_station, station_to_main, combinedDict)
    )   # Parameters: (caption, size, pos, queue_in, queue_out, images)

    # Begin both processes to start windows
    ride_park.start()
    theme_park.start()

    try: # Main loop to keep program running and route messages between windows
        while theme_park.is_alive(): # Check if the main window is currently open
            
            # Route messages FROM Park TO Station
            try:
                msg = park_to_main.get_nowait() # Grabs the most recent message in queue
                main_to_station.put(msg)
            except:
                pass
    
            # Route messages FROM Station TO Park
            try:
                msg = station_to_main.get_nowait() # Grabs the most recent message in queue
                main_to_park.put(msg)
            except:
                pass

    except KeyboardInterrupt: # Allow user to exit program with Ctrl+C in terminal
        pass

    finally: # Terminate all processes and close all windows
        print("\nEnding Program...")
        
        print("\nClosing Station Window Process...")
        ride_park.terminate()
        print("\nStation Window is closed.")

        print("\nClosing Main Window Process...")
        theme_park.terminate()
        print("\nMain Window is closed.")