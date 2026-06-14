# Import all necessary libraries and modules
# Multiprocessing is used to create separate processes running simultaneously
from multiprocessing import Queue, Process

# Import the classes for the main window and second information window
from firstWindow import ParkWindow
from secondWindow import RideWindow

# Import essential variables
from initialization import config
from randomLogs import random_log
from dataLogs import random_logs
from dataLogs import given_logs

# Function to start the main window for theme park using theme_park process
def start_park_window(caption, size, pos, queue_in, queue_out, images):
    park_window = ParkWindow(caption, size, pos, queue_in, queue_out, images)
    park_window.run()

# Function to start the second window for station information using ride_park process
def start_ride_window(caption, size, pos, queue_in, queue_out, random_data, given_data):
    ride_window = RideWindow(caption, size, pos, queue_in, queue_out, random_data, given_data)
    ride_window.run()

# Run program if this file is being run directly
if __name__ == "__main__":
    
    # Create IN/OUT queues for Theme Park
    main_to_park = Queue()
    park_to_main = Queue()

    # Create a dedicated kwargs dictionary for the first window process
    park_kwargs = {
        **config['parkWindow'],
        'queue_in': main_to_park,
        'queue_out': park_to_main,
        'images': config['images']
    }

    # Create IN/OUT queues for Station
    main_to_ride = Queue()
    ride_to_main = Queue()
    
    # Create a dedicated kwargs dictionary for the second windo process
    ride_kwargs = {
        **config['rideWindow'],
        'queue_in': main_to_ride,
        'queue_out': ride_to_main,
        'random_data' : random_logs,
        'given_data' : given_logs
    }

    # Create Main Window with communcation_queue
    park_process = Process(
        target=start_park_window, # Target function to start the main window for theme park
        kwargs=park_kwargs
    )

    # Create Main Window with communcation_queue
    ride_process = Process(
        target=start_ride_window, # Target function to start the main window for theme park
        kwargs=ride_kwargs
    )
    
    # Begin both processes to start windows
    park_process.start()
    ride_process.start()

    try: # Main loop to keep program running and route messages between windows
        while park_process.is_alive(): # Check if the main window is currently open
            
            # Route messages FROM Park TO Ride
            try:
                msg = park_to_main.get_nowait() # Grabs the most recent message in queue
                main_to_ride.put(msg)
            except:
                pass
    
            # Route messages FROM Ride TO Park
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
        ride_process.terminate()
        print("Ride Window is closed.")

        print("\nClosing Park Window Process...")
        park_process.terminate()
        print("\nPark Window is closed.")
        