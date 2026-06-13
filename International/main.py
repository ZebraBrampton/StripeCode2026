# Import all necessary libraries and modules
# Multiprocessing is used to create separate processes running simultaneously
from multiprocessing import Queue, Process

# Import the classes for the main window and second information window
from firstWindow import ParkWindow
from secondWindow import RideWindow

# Import the config with all essential variables
from initialization import config

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

    # Create IN/OUT queues for Theme Park
    main_to_park = Queue()
    park_to_main = Queue()

    # Create IN/OUT queues for Station
    main_to_ride = Queue()
    ride_to_main = Queue()

    # Create Main Window with communcation_queue
    theme_park = Process(
        target=start_theme_park, # Target function to start the main window for theme park
        args=(  # Parameters: (caption, size, pos, queue_in, queue_out, images)
            config['parkWindow']['caption'],
            (config['parkWindow']['width'], config['parkWindow']['height']), 
            (config['parkWindow']['pos_x'], config['parkWindow']['pos_y']), 
            main_to_park, 
            park_to_main, 
            config['images']
            )
    )

    # Create Main Window with communcation_queue
    ride_park = Process(
        target=start_ride_window, # Target function to start the main window for theme park
        args=(  # Parameters: (caption, size, pos, queue_in, queue_out)
            config['rideWindow']['caption'],
            (config['rideWindow']['width'], config['parkWindow']['height']), 
            (config['rideWindow']['pos_x'], config['parkWindow']['pos_y']), 
            main_to_ride, 
            ride_to_main,
            )
    )

    # Begin both processes to start windows
    ride_park.start()
    theme_park.start()

    try: # Main loop to keep program running and route messages between windows
        while theme_park.is_alive(): # Check if the main window is currently open
            
            # Route messages FROM Park TO Station
            try:
                msg = park_to_main.get_nowait() # Grabs the most recent message in queue
                main_to_ride.put(msg)
            except:
                pass
    
            # Route messages FROM Station TO Park
            try:
                msg = ride_to_main.get_nowait() # Grabs the most recent message in queue
                main_to_park.put(msg)
            except:
                pass

    except KeyboardInterrupt: # Allow user to exit program with Ctrl+C in terminal
        pass

    finally: # Terminate all processes and close all windows
        print("\nEnding Program...")
        
        print("\nClosing Ride Window Process...")
        ride_park.terminate()
        print("\Ride Window is closed.")

        print("\nClosing Park Window Process...")
        theme_park.terminate()
        print("\nPark Window is closed.")