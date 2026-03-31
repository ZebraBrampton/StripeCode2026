from os import environ
from multiprocessing import Queue, Process

from themeParkClass import ParkWindow
from rideClass import RideWindow

from bhavsCode import combinedDict

def start_theme_park(caption, size, pos, comm_queue, images):

    park_window = ParkWindow(caption, size, pos, comm_queue, images)
    park_window.run()

def start_ride_window(caption, size, pos, comm_queue, logs):
    
    ride_window = RideWindow(caption, size, pos, comm_queue, logs)
    ride_window.run()
    


if __name__ == "__main__":

    # Image class
    images = {

        "Map" : ("Map", (0, 0)),

        "Lazy River" : ("Lazy River", (454, 647)),

        "Nebula Spinner" : ("Nebula Spinner", (459, 8)),

        "Pixel Arcade" : ("Pixel Arcade", (25, 532)),

        "Rocket Slingshot" : ("Rocket Slingshot", (189, 8)),

        "Splashing Mountain" : ("Splashing Mountain", (478, 180)),

        "Titan Coaster" : ("Titan Coaster", (17, 275)),

        "Hydration Station" : ("Hydration Station", (450, 524)),

        "Pixel Popcorn" : ("Pixel Popcorn", (253, 180)),

        "Quantum Cafe" : ("Quantum Cafe", (176, 673)),

        "The Sugar Shack" : ("The Sugar Shack", (244, 523))

    }

    # Create the communication pipe
    theme_park_queue = Queue()

    # Create Main Window with communcation_queue
    theme_park = Process(
        target=start_theme_park,
        args=("Theme Park", (800, 900), (10, 45), theme_park_queue, images)
    )
    theme_park.start()

    # Create the second communication pipe
    station_queue = Queue()

    # Create Second Information Window with communcation_queue
    ride_park = Process(
        target=start_ride_window,
        args=("Station", (400, 900), (820, 45), station_queue, combinedDict)
    )
    ride_park.start()

    try:
        while theme_park.is_alive(): # Check if the main window is currently open
            
            if not theme_park_queue.empty(): # Checks if the message queue is NOT empty
                msg = theme_park_queue.get() # Grabs the most recent message in queue

                station_queue.put(msg)
                

        theme_park.join()

    except KeyboardInterrupt:
        pass

    finally:
        print("\nEnding Program...")
        
        print("\nClosing Station Window Process...")
        ride_park.terminate()
        print("\nStation Window is closed.")

        print("\nClosing Main Window Process...")
        theme_park.terminate()
        print("\nMain Window is closed.")